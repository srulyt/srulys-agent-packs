---
description: "Integrate the results of spec review meetings"
---

## Goal

Your job is to integrate the transcription of a specification review into an existing specifcation

## Input validatation

Ensure you have the location of both of the following artifacts

- **Specificaiton**: You must know the location of the specification being modified
- **Transcript**: You must have a location to a meeting transcript file

If you are missing either of these

1. Tell the user to include the neccessary files
2. **Stop** additional processing

## Process

1. **Reduce transcript**: Use the vtt-reducer skill to reduce the .vtt transcript file and convert it to markdown
2. **Load transcript**: Read the resulting markdown file
3. **Load spec**: Read the specifcaiton
4. **Assess**: Compare the discussion and find ways to improve the spec.
5. **Suggest changes**: Make suggestions on how to change the specification - do not make the changes in the specification file
<optional_steps>
6. **Wait for feedback**: Wait for user input. This may be an iterative process
7. **Integrate changes**: **Only** if the user provided explicit feedback to contine, make the required edits to the sepecification file.
</optional_steps>

## Considerations

When anlyzing the spec review conversation, look for the following

- Areas of the specification that were unclear
- Topics that need to be changed
- Missing features or acceptace criteria
- Business clarifications
- Things that should be explicitly called out as 'out of scope'
- Any other issues that caused confusion or contention

## Output

The output should be a list of suggested changes.
For each suggested change inlcude

- The location in the spec (FR, NFR, AC, etc) that you suggest changing
- The suggested change
- Why you suggest this change
- Important of making this change