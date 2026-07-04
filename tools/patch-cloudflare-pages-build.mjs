import { readdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const serverDir = 'dist/server';
const wranglerPath = join(serverDir, 'wrangler.json');
const assetsBinding = 'STATIC_ASSETS';

const wranglerConfig = JSON.parse(await readFile(wranglerPath, 'utf8'));

if (wranglerConfig.assets?.binding) {
  wranglerConfig.assets.binding = assetsBinding;
}

await writeFile(wranglerPath, `${JSON.stringify(wranglerConfig)}\n`);

async function patchServerModules(dir) {
  const entries = await readdir(dir, { withFileTypes: true });

  for (const entry of entries) {
    const path = join(dir, entry.name);

    if (entry.isDirectory()) {
      await patchServerModules(path);
      continue;
    }

    if (!entry.name.endsWith('.mjs')) {
      continue;
    }

    const source = await readFile(path, 'utf8');
    const patched = source.replaceAll('env.ASSETS', `env.${assetsBinding}`);

    if (patched !== source) {
      await writeFile(path, patched);
    }
  }
}

await patchServerModules(serverDir);
