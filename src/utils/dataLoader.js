import fs from 'fs/promises';

export const loadEventsData = async (jsonPath) => {
  const jsonContent = await fs.readFile(jsonPath, 'utf-8');
  return JSON.parse(jsonContent);
};
