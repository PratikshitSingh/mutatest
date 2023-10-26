import subprocess
from pathlib import Path

def get_git_difference(git_location: Path, git_commit: list):

    showline_path = Path('../showlinenum.awk').resolve()

    commit1 = ''
    commit2 = ''

    if len(git_commit) == 2:
        commit1, commit2 = git_commit
    elif len(git_commit) == 1:
        commit1 = git_commit[0]

    cmd = f'git diff -U0 {commit1} {commit2} | "{showline_path}" show_path=1 show_hunk=0 show_header=0'
    print(cmd)

    print(git_location.resolve())

    result = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=git_location.resolve(), shell=True)
    result.wait()

    if result.returncode == 0:
        git_diff_hashmap = {}

        for line in result.stdout:
            line = line.decode()
            path, line_num, line_change = line.split(':')

            if line_change.startswith('+'):
                if path not in git_diff_hashmap:
                    git_diff_hashmap[path] = []
                
                git_diff_hashmap[path].append(int(line_num))

        print(git_diff_hashmap)
    else:
        raise Exception('Cannot successfully compute the git diff.')

    cmd = 'git ls-files --others --exclude-standard'

    result = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=git_location.resolve(), shell=True)
    result.wait()

    if result.returncode == 0:
        git_untracked_files = []

        for line in result.stdout:
            line = line.decode()
            line = line.strip(' \n')
            git_untracked_files.append(line)

        print(git_untracked_files)

    else:
        raise Exception('Cannot successfully compute git untacked files.')



def filter_sample_space(sample_space):
    pass