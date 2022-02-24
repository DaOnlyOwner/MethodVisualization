from ast import literal_eval as make_tuple
from pathlib import Path
from PIL import Image
from wordcloud import WordCloud
import yaml

wordcloud_all_settings = dict(
    width=1024,
    height=768,
    relative_scaling=0.3,
    min_font_size=10,
    max_font_size=100,
    max_words=1000,
    prefer_horizontal=0.9,
    background_color="white",
)

wordcloud_cluster_settings = dict(
    width=400,
    height=300,
    relative_scaling=0.3,
    min_font_size=10,
    max_font_size=100,
    max_words=1000,
    prefer_horizontal=0.9,
    background_color="white",
)


def read_analysis_classes(results_directory):
    words_and_data = {}
    with open(results_directory / '2analysis_classes.txt', 'r') as concepts_and_counts:
        for line in concepts_and_counts:
            tuple = make_tuple(line)
            word = tuple[0]
            data = tuple[1]
            words_and_data[word] = data
    return words_and_data


class SimpleGroupedColorFunc(object):
    """Create a color function object which assigns EXACT colors
       to certain words based on the color to words mapping

       Parameters
       ----------
       color_to_words : dict(str -> list(str))
         A dictionary that maps a color to the list of words.

       default_color : str
         Color that will be assigned to a word that's not a member
         of any value from color_to_words.
    """

    def __init__(self, color_to_words, default_color):
        self.word_to_color = {word: color
                              for (color, words) in color_to_words.items()
                              for word in words}

        self.default_color = default_color

    def __call__(self, word, **kwargs):
        return self.word_to_color.get(word, self.default_color)


def cluster_color(idx, num_clusters):
    max_color = 16 ** 6
    min_color = 0
    step_size = max_color / num_clusters
    color = '#' + hex(int(min_color + idx * step_size))[2:].zfill(6)
    return color

def visualize_wordcloud(results_directory):
    default_color = 'grey'

    words_and_data = read_analysis_classes(results_directory)
    frequencies = dict((word, data['count']) for (word, data) in words_and_data.items())

    cluster_files = results_directory.glob(f'4clusters-*.yml')
    for cluster_file in cluster_files:
        with open(cluster_file, 'r') as document:
            clusters = yaml.safe_load(document)

            num_clusters = len(clusters)

            color_to_words = dict(
                (cluster_color(index, num_clusters), cluster_members) for index, cluster_members in enumerate(clusters))

            grouped_color_func = SimpleGroupedColorFunc(color_to_words, default_color)
            word_cloud(
                frequencies,
                f'{num_clusters}_ALL',
                results_directory,
                color_func=grouped_color_func,
                wordcloud_settings=wordcloud_all_settings,
            )

            for cluster_number, cluster_members in enumerate(clusters):
                try:
                    cluster_subset = dict((member, frequencies[member]) for member in cluster_members)
                except:
                    continue

                word_cloud(
                    cluster_subset,
                    f'{num_clusters}_{cluster_number}',
                    results_directory,
                    color_func=grouped_color_func,
                    wordcloud_settings=wordcloud_cluster_settings,
                )


def word_cloud(frequencies, outfile_suffix, results_directory, color_func=None,
               wordcloud_settings={}):
    # Create and generate a word cloud image:
    wordcloud = WordCloud(**wordcloud_settings).generate_from_frequencies(frequencies)

    if color_func:
        wordcloud.recolor(color_func=color_func)

    # Display the generated image:
    # plt.figure()
    # plt.imshow(wordcloud, interpolation="bilinear")
    # plt.axis("off")
    # plt.show()

    wordclouds_directory = ((results_directory) / 'wordclouds')
    wordclouds_directory.mkdir(parents=True, exist_ok=True)
    wordcloud.to_file(wordclouds_directory / f'word_cloud_{outfile_suffix}.png')
    # TODO: fix SVG export
    # wordcloud.to_svg(wordclouds_directory / f'word_cloud_{outfile_suffix}.svg')


def main():
    visualize_wordcloud(Path("../example_input"))

if __name__ == "__main__":
    main()

