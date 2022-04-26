# Fast-forward Action

An action that enables a pull request to be merged using `--fast-forward` to avoid creating a merge commit on the target branch.

Usage should be within a workflow that has access to the `${{ github.event.issue }}` object related to the pull request. An example of this is below in which you can use a comment on a pull request to trigger the condition:

## Usage

```yaml
name: FF Merge

on: 
  issue_comment:
    types: [created]

jobs:
  ff-merge:
    runs-on: ubuntu-latest
    if: github.event.issue.pull_request != '' && contains(github.event.comment.body, '/fast-forward')
    steps:
      - name: Fast Forward
        uses: ndustrialio/actions/ffmerge@main
        with:
          token: ${{ secrets.GH_ADMIN_TOKEN }}
```