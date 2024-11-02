.PHONY: env
env:
	source '.env/bin/activate'

.PHONY: codewars
codewars:
  ifdef URL
    docker-compose run --rm scraper $(URL)
  else
    @echo "Please provide a URL. Usage: make run URL=\"https://www.codewars.com/kata/example\""
  endif
