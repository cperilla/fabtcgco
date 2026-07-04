import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const postsCollection = defineCollection({
  loader: glob({ base: "./src/content/posts", pattern: "**/*.{md,mdx}" }),
  schema: z.object({
    title: z.string(),
    author: z.string(),
    description: z.string().optional(),
    publishDate: z.date(),
  }),
});

export const collections = {
  posts: postsCollection, // <- THIS MUST BE 'posts' to match src/content/posts/
};
