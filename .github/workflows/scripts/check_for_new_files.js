async function fetchAddedFiles(github, context) {
  const {
    issue: { number: issue_number },
    repo: { owner, repo }
  } = context;

  return github.paginate(
    'GET /repos/{owner}/{repo}/pulls/{pull_number}/files',
    { owner, repo, pull_number: issue_number },
    (response) => response.data.filter((file) => file.status === 'added')
  );
}

module.exports = {
  getAddedFiles: async ({ github, context }) => {
    return fetchAddedFiles(github, context);
  },

  getAddedFilesCount: async ({ github, context }) => {
    const files = await fetchAddedFiles(github, context);
    return files.length;
  },

  validateCodeowners: async ({ github, context, fetch, ignore }) => {
    const { CURRENT_BRANCH, CURRENT_REPO } = process.env;
    const addedFiles = await fetchAddedFiles(github, context);

    const codeownersFile = `https://raw.githubusercontent.com/${CURRENT_REPO}/${CURRENT_BRANCH}/.github/CODEOWNERS`;

    console.log('Fetching CODEOWNERS from: ', codeownersFile);

    const response = await fetch(codeownersFile);
    const body = await response.text();

    const codeownersFilePatterns = body
      .split('\n')
      .filter((e) => !e.startsWith('#'))
      .filter((e) => e.length > 1)
      .map((e) => e.split(/\s+/)[0]);

    console.log(
      'CODEOWNERS patterns to match new files against: ',
      codeownersFilePatterns
    );

    const ig = ignore().add(codeownersFilePatterns);

    const filesNotInCodeowners = [];

    addedFiles.forEach((newFile) => {
      if (!ig.ignores(newFile.filename)) {
        console.log(`${newFile.filename} is not covered by CODEOWNERS`);
        filesNotInCodeowners.push(newFile.filename);
      }
    });

    const {
      issue: { number: issue_number },
      repo: { owner, repo }
    } = context;

    console.log('New files not in CODEOWNERS: ', filesNotInCodeowners);

    if (filesNotInCodeowners.length > 0) {
      const files = filesNotInCodeowners.map((e) => `- ${e}\n`).join('');

      const needCodeownersUpdateComment = `CODEOWNERS need to be updated because these new files are not covered:\n ${files}`;
      github.rest.issues.createComment({
        owner,
        repo,
        issue_number,
        body: needCodeownersUpdateComment
      });
      const labels = ['update-codeowners'];
      github.rest.issues.addLabels({ owner, repo, issue_number, labels });
    }
  }
};
