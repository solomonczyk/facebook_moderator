# Language Policy

## Output Languages

| Context | Language |
|---------|----------|
| Public Facebook post | Serbian |
| Reply to author | Serbian |
| Operator summary | Russian |
| Classification labels | English |
| Reason field | English |
| Audit entries | English |

## Input Languages

The agent must understand:
- Serbian (Latin and Cyrillic)
- Russian
- Ukrainian
- Hungarian
- Romanian
- English
- Mixed text

## Serbian Rules

- Use Latin script for public posts
- Preserve phone numbers exactly as written
- Do not translate names
- Do not invent locations
- Use standard seasonal work vocabulary

## Russian Rules

- Operator summary only, never public
- Short: 1-2 sentences
- Include: what the post is, key missing info, recommended action

## Phone Numbers

- Never change phone number format
- Preserve +381, 0, spaces, dashes as in source
- If no phone visible, mark as missing, do not invent
