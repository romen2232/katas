# Use the official PHP 8.1 CLI image as the base
FROM php:8.1-cli

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive

# Install only necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  libpq-dev \
  libicu-dev \
  libpng-dev \
  libzip-dev \
  zlib1g-dev \
  unzip \
  && docker-php-ext-install pdo_pgsql intl exif bcmath zip gd \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Composer globally
COPY --from=composer:2.5 /usr/bin/composer /usr/bin/composer

# Set Composer's global bin directory to PATH
ENV PATH="/root/.composer/vendor/bin:${PATH}"

# Install PHPUnit globally using Composer
RUN composer global require phpunit/phpunit --prefer-dist --no-progress --no-suggest

# Copy your custom PHP configuration if needed
# Ensure you have a php.ini file inside your php folder
COPY php/php.ini /usr/local/etc/php/conf.d/

# Set the working directory to the 'php' folder
WORKDIR /var/www/php

# Optional: Mount the 'php' folder as a volume for real-time code changes
VOLUME /var/www/php

# Adjust permissions for the www-data user (optional)
RUN usermod -u 1000 www-data && \
  groupmod -g 1000 www-data && \
  chown -R www-data:www-data /var/www/php

# Set the default command to run PHPUnit tests
CMD ["phpunit"]
