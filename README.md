# Development

## Dependency management

The project makes use of Poetry for dependency management. To install the dependencies, run:

```bash
poetry install
```

When adding or removing dependencies, make sure to also update the requirement.txt file by running:

```bash
poetry export --without-hashes --format=requirements.txt --output=requirements.txt
```

## CSS

Ensure to compile the SCSS files to CSS by running:

```bash
python sass_compile.py
```

IMPORTANT: The CSS file needs to be compiled and committed to the repository. The application will look like shit otherwise.

## Git-hook
A git-hook is added to do the poetry export and the SCSS compilation with each commit.

# Deployment

## Docker
The docker image gets created and pushed to the docker hub repository by the GitHub Actions workflow. The tag will only be set to 'latest' when a tag is created. Otherwise the latest version is available through the 'stable-main' tag. The image can be pulled and run using the following command:

```bash
docker run -p 5173:5173 --name luminasync --env-file /path/to/.env -v /path/to/your/db-folder:/app/db bertoja/luminasync-v2:stable-main
```
## Environment variables

The environment variables are stored in a .env file. The following variables are required:

```bash
TAPO_USERNAME
TAPO_PASSWORD
OPENAI_API_KEY
NEWSDATA_API_KEY
```
