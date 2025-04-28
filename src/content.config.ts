import { defineCollection, z } from "astro:content";

const postsCollection = defineCollection({
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
