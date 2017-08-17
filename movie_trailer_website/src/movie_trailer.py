import media
import trailer_website


# create instances of movies
dangal = media.Movie(
    "Dangal", "Former wrestler trains his daughters", "https://upload." +
    "wikimedia.org/wikipedia/en/9/99/Dangal_Poster.jpg", "https://www." +
    "youtube.com/watch?v=x_7YlGv9u1g"
 )

bahubali2 = media.Movie(
    "Baahubali2: The Conclusion", "Shiva, the son of Bahubali, begins to " +
    "search for answers", "https://upload.wikimedia.org/wikipedia/en/f/f9/" +
    "Baahubali_the_Conclusion.jpg", "https://www.youtube.com/watch?" +
    "v=G62HrubdD6o"
)

titanic = media.Movie(
    "Titanic", "Epic movie on the ill-fated maiden voyage of the Titanic " +
    "ship", "https://upload.wikimedia.org/wikipedia/en/2/22/Titanic_poster." +
    "jpg", "https://www.youtube.com/watch?v=2e-eXJ6HgkQ"
)

avatar = media.Movie(
    "Avataar", "A marine on an alien planet", "https://upload.wikimedia.org/" +
    "wikipedia/en/b/b0/Avatar-Teaser-Poster.jpg", "https://www.youtube.com/" +
    "watch?v=d1_JBMrrYw8"
)

pulp_fiction = media.Movie(
    "Pulp Fiction", "Pulp Fiction", "https://upload.wikimedia.org/wikipedia/" +
    "en/3/3b/Pulp_Fiction_%281994%29_poster.jpg", "https://www.youtube.com/" +
    "watch?v=s7EdQ4FqbhY"
)

# add movie instances to a list
movies = [avatar, dangal, pulp_fiction, titanic, bahubali2]
# pass the movie list to the trailer website method that
# renders the movies to UI
trailer_website.open_movies_page(movies)
