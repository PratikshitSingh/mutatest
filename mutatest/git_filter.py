import subprocess
from pathlib import Path
import os

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

            full_path = str(os.path.join(git_location.resolve(), path))

            if line_change.startswith('+'):
                if full_path not in git_diff_hashmap:
                    git_diff_hashmap[full_path] = []
                
                git_diff_hashmap[full_path].append(int(line_num))

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
            full_path = str(os.path.join(git_location.resolve(), line))
            git_untracked_files.append(full_path)

    else:
        raise Exception('Cannot successfully compute git untacked files.')

    return (git_diff_hashmap, git_untracked_files)



def filter_sample_space(sample_space, git_diff_hashmap, git_untracked_files, git_location):
    
    filtered_samples = []

    for sample in list(sample_space):
        mutation_target_path = sample.source_path.resolve()
        line_num = int(sample.loc_idx.lineno)

        if mutation_target_path in git_untracked_files:
            filtered_samples.append(sample)
        elif mutation_target_path in git_diff_hashmap and line_num in git_diff_hashmap[mutation_target_path]:
            filtered_samples.append(sample)
    
    return filtered_samples
        