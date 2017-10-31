#!/usr/bin/env python
import psycopg2
import datetime

# Query for most popular 3 articles of all time
popularArticlesSQL = (
    " SELECT a.title, maxes.num "
    " FROM articles a"
    " JOIN "
    " (SELECT path, count(*) as num "
    " FROM log GROUP BY path) "
    " AS maxes "
    " ON substring(maxes.path,10) = a.slug "
    " ORDER BY maxes.num DESC LIMIT 3; "
)

# Query for most popular article authors of all time
popularAuthorsSQL = (
    " SELECT distinct b.name, sum(maxes.num) "
    " FROM articles a "
    " JOIN "
    " (SELECT path, count(*) as num "
    " FROM log GROUP BY path) "
    " AS maxes "
    " ON substring(maxes.path,10) = a.slug "
    " JOIN authors b "
    " ON a.author = b.id "
    " GROUP BY b.name "
    " ORDER BY sum(maxes.num) DESC; "
)

# Query for days with more than 1% of requests lead to errors
errorRequestsSQL = (
    " SELECT to_char(FILTER.day, 'FMMonth FMDD, YYYY'), FILTER.pct "
    " FROM "
    " (SELECT ALL_RQ.day AS day, "
    " 100.0 * BAD_RQ.num / ALL_RQ.num AS pct "
    " FROM "
    " (SELECT time::date AS day, count(*) AS num "
    " FROM log WHERE status != '200 OK' "
    " GROUP BY time::date ) AS BAD_RQ "
    " JOIN "
    " (SELECT time::date AS day, count(*) AS num "
    " FROM log "
    " GROUP BY time::date ) AS ALL_RQ "
    " ON BAD_RQ.day = ALL_RQ.day "
    " ) AS FILTER "
    " WHERE FILTER.pct > 1; "
)


def get_results(query):
    """ Return results of the query from 'news database' """
    db = psycopg2.connect(database="news")
    c = db.cursor()
    c.execute(query)
    results = c.fetchall()
    db.close()
    return results


print("#####    Most popular 3 articles of all time  ##### ##### ##### #####")

results = get_results(popularArticlesSQL)
for row in results:
    print('"{}" - {} views'.format(row[0], row[1]))

print
print("#####    Most popular article authors of all time   ##### ##### #####")

results = get_results(popularAuthorsSQL)
for row in results:
    print('{} - {} views'.format(row[0], row[1]))

print
print("#####    Days with more than 1% of requests lead to errors ##### ####")

results = get_results(errorRequestsSQL)
for row in results:
    error_pcnt = str("{0:.2f}".format(round(row[1], 2)))
    print(str(row[0]) + ' - ' + error_pcnt + '% errors')
