FROM python:3.12-alpine

ENV OUTPUT_JSON_PATH /out/properties.json
ENV DB_PATH /out/properties.db
ENV LOG_FILE_PATH /out/rightmove.log
ENV NO_DB 0

RUN mkdir "/rightmove-scraper"

WORKDIR /rightmove-scraper

ADD requirements.txt run.sh scrapy.cfg ./
ADD rightmove_scraper ./rightmove_scraper

RUN pip install --no-cache-dir -r requirements.txt

# Runs the scraper every day at 8pm
RUN echo "* 20 * * * cd /rightmove-scraper && ./run.sh" >> /etc/crontabs/root

# Run scraper immediately
CMD "./run.sh"

# Then enter cron mode
CMD ["crond", "-f"]
