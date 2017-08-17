import webbrowser


class Movie():
    """
    Movie class stores movie properties and provides an API to show the movie trailer
    """
    def __init__(self, movie_title, movie_storyline, poster_image,
                 trailer_youtube):
        """
        constructor initializes the following movie properties:
        title of the movie
        story line
        url to the poster image
        movie trailer link on youtube
        """
        self.title = movie_title
        self.storyline = movie_storyline
        self.poster_image_url = poster_image
        self.trailer_youtube_url = trailer_youtube

    def show_trailer(self):
        """
        open the movie trailer in a webbrowser
        """
        webbrowser.open(self.trailer_youtube_url)
