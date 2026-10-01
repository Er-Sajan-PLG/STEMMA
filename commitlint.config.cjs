module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    // `merge` and `state` are repository-specific additions to the Conventional
    // Commits type list:
    //   merge — merge commits on this repo are meaningful units of work.
    //   state — required by the Multi-Agent Coordination Protocol
    //           (state/PROTOCOL.md §Shutdown step 6), which specifies
    //           `state: <agent-id> session <session-id>` for coordination-state
    //           commits. Without it here, every MACP shutdown commit would fail
    //           this required status check, forcing agents to either deviate
    //           from the protocol or rewrite history. See
    //           state/conflicts/CONFLICT-002-protocol-commit-type.md.
    "type-enum": [2, "always", ["feat", "fix", "docs", "style", "refactor", "perf", "test", "build", "ci", "chore", "revert", "merge", "state"]],
    "subject-case": [0],
    "body-max-line-length": [0],
    "footer-max-line-length": [0],
    "header-max-length": [0],
  },
};
