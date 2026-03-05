interface StmSourceFile {
  path: string;
  content?: string;
}

export function extractStmGitignoreEntries(files: StmSourceFile[]): string[] {
  const stmDirs = new Set<string>();
  const stmPattern = /\.[A-Za-z0-9-]*stm\//g;

  for (const file of files) {
    const pathMatches = file.path.match(stmPattern) || [];
    for (const match of pathMatches) {
      stmDirs.add(match);
    }

    if (file.content) {
      const contentMatches = file.content.match(stmPattern) || [];
      for (const match of contentMatches) {
        stmDirs.add(match);
      }
    }
  }

  return [...stmDirs];
}