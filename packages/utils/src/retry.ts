export async function withRetry<T>(fn: () => Promise<T>, opts = {maxAttempts:3,baseDelayMs:500,maxDelayMs:10000,factor:2}): Promise<T> {
  let last: unknown;
  for (let i = 1; i <= opts.maxAttempts; i++) {
    try { return await fn(); } catch (e) {
      last = e;
      if (i === opts.maxAttempts) break;
      const delay = Math.min(opts.baseDelayMs * Math.pow(opts.factor, i-1), opts.maxDelayMs);
      await new Promise(r => setTimeout(r, delay + Math.random()*100));
    }
  }
  throw last;
}
