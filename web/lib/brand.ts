export function isSensiaEnterprise(name: string) {
  return /(^|\s)SENSIA(\s|$)/i.test(name);
}
