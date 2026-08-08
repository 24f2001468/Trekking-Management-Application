export function getRandomTrekImage(trekId) {
  // Use picsum.photos to generate a deterministic random image based on trek ID
  // This does not store any image; it returns a URL that can be used directly in <img> src attributes.
  // Width 200px, height 120px – adjust as needed.
  const width = 200;
  const height = 120;
  // Using the trekId as seed ensures consistency across renders.
  return `https://picsum.photos/seed/${encodeURIComponent(trekId)}/${width}/${height}`;
}
