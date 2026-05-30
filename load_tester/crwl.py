"""
Let's see what we can from this so we can implement in the load tester .
First we need some kind of while loop to iterate and produced the make_single_req . ? 
ok this could be one way ? what is any other way we could do this ? 


"""



#         async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
#             while self.frontier and self.pages_crawled < self.config.max_pages:
#                 current_depth = self.frontier[0][1]
#                 if current_depth > self.config.max_depth:
#                     break
#
#                 current_url: list[str] = []
#                 while self.frontier and self.frontier[0][1] == current_depth:
#                     url, _ = self.frontier.popleft()
#                     normal = self._normalize_outgoing_links(url)
#                     current_url.append(normal)
#
#                 # To limit the Number of concurrent callbacks in the event loop
#                 sem = asyncio.Semaphore(self.config.concurrency)
#
#                 # 
#                 tasks = [fetch_pages(session, url, sem) for url in current_url]
#                 results = await asyncio.gather(*tasks, return_exceptions=True)
#
#                 for urls_set in results:
#                     if isinstance(urls_set, Exception):
#                         self._append_jsonl(self.errors_jsonl, {
#                             "timestamp": utc_now(),
#                             "depth": current_depth,
#                             "ok": False,
#                             "error": repr(urls_set),
#                         })
#                         summary["errors"] += 1
#                         continue
#
#                     self.pages_crawled += 1
#
#                     for child in urls_set:
#                         if self.pages_crawled >= self.config.max_pages:
#                             break
#                         if child not in self.visited:
#                             self.visited.add(child)
#                             self.frontier.append((child, current_depth + 1))
#                             self._append_jsonl(self.edges_jsonl, {
#                                 "timestamp": utc_now(),
#                                 "parent": url,
#                                 "child": child,
#                                 "parent_depth": current_depth,
#                                 "child_depth": current_depth + 1,
#                             })
#                     summary["pages_crawled"] = self.pages_crawled
#                     summary["discovered_urls"] = len(self.visited)
#
#             summary["finished_at"] = utc_now()
#             summary_path = self.meta_dir / "summary.json"
#             summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
#             return summary
#
#
# async def main():
#     config = CrawlerConfig(
#         start_url="https://techcrunch.com",
#         output_dir="crawl_output",
#         max_depth=3,
#         max_pages=200,
#         concurrency=20,
#
