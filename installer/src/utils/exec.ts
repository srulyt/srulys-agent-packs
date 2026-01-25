import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function execCommand(command: string): Promise<string> {
  try {
    const { stdout } = await execAsync(command);
    return stdout.trim();
  } catch (error) {
    throw new Error(`Command failed: ${command}`);
  }
}

export async function execWithInput(command: string, input: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const proc = exec(command, (error, stdout) => {
      if (error) {
        reject(error);
      } else {
        resolve(stdout.trim());
      }
    });
    
    if (proc.stdin) {
      proc.stdin.write(input);
      proc.stdin.end();
    }
  });
}

export async function commandExists(command: string): Promise<boolean> {
  try {
    await execCommand(`${process.platform === 'win32' ? 'where' : 'which'} ${command}`);
    return true;
  } catch {
    return false;
  }
}