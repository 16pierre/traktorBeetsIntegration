# Traktor custom tags: Beets Integration

This project is an integration between [Beets](https://github.com/beetbox/beets) 
and Traktor that helps manage Traktor libraries.

**Warning:** this was developped and used only on MacOs, I doubt this project is compatible with Windows. 
This project comes with no guarantees: I recommend backing-up your files.

Core features (detailed in [Features](#Features)):
- enable usage of custom tags in Traktor through auto-generated playlists
- write comments on Traktor tracks that list custom tags
- utils to import Traktor library into Beets' library
- sync tags between Traktor and Beets

Planned features:
- multi-value metadata support
- create an issue if you have a feature request ;)

To better understand how this project was born, see the [Motivations section](#Motivations).

Feel free to contribute with PRs/issues !

## Install

This projects was developed `pipenv` + `python 3.8`.

```
git clone https://github.com/16pierre/traktorPlaylistExport
cd traktorPlaylistExport
pipenv install
```

## Configuration
```
cp locations.json.template locations.json
```

1. Edit `locations.json` to specify where your `Traktor` `collection.nml` file is etc.
2. Edit `scanner_tags.json` to specify the different custom tags you want to use & playlists you want to generate
3. For import utils: edit `Beets` config: set `import.link: yes` (see [below](#configuration-required))

## Usage


### Sync Traktor<->Beets
```
pipenv run sync
```

### Utils: tag scanner
Helps you scan your tracks with tags specified in `scanner_tags.json`.
You can also use `beet modify`, but most of the time I find it more convenient to use the scanner to avoid typos.
```
pipenv run scan
pipenv run scan artist:Daft Punk
etc.
```


### Utils: import helper
Helps you import your `Traktor` library inside `Beets`. See below for more explanation, this is not trivial.
```
pipenv run import
```

## Features

### Sync Beets<->Traktor

In this section, let's assume that tracks are imported in both `Beets` and `Traktor`, 
and that they both use the same file paths.

The core idea here is the link between `Traktor`'s playlists and `Beets` metadata. Let's take a few examples.

Say I configured `scanner_tags.json` with:
```
{
    "_playlists": [
        ["mood"],
        ["energy"],
        ["mood", "energy"]
    ],
    "mood": ["dark", "joyful"],
    "energy": ["1", "2", "3", "4", "5"]
} 
```

This will create 3 kinds of playlists in `Traktor`:
- one for each `mood`: `mood: dark`...
- one for each `energy`: `energy: 1`...
- one for each `(mood, energy)` couple: `mood: dark, energy: 1` 

Note:
- to avoid noise, this won't create playlists if they are empty
- to keep playlists sorted in Traktor, a prefix is added to the playlist name to match the order in `_playlists` 

With this system, we can unambiguously link `Beets metadata` to `Traktor playlists`; 
this link is the core mechanism behind the sync:
1. Editing a tag in `Beets` will update the matching `Traktor` playlists
2. Adding a track to a `Traktor` playlist will update the corresponding tags in `Beets`

Extra mechanisms:
- you can use the star rating system in `Traktor`, it's synced with the `rating` tag in `Beets`.
- to help you visualize the metadata in `Traktor`, the sync writes comments on the Track to list the custom tags 
(warning: this will override existing comments, 
will be fixed, issue: https://github.com/16pierre/traktorPlaylistExport/issues/1)


### Help import Traktor library into Beets

#### Configuration required

**Note:** this util requires using `beet import` with symlinks. You therefore need to configure `Beets` like this:
```
import:
    link: yes
``` 
For more details, see [Beets docs](https://beets.readthedocs.io/en/stable/reference/config.html#link).

#### Why add utils for imports
In order for the sync to work properly, you need to have imported the tracks in both `Traktor` and `Beets`.

Importing `Beets`' library in `Traktor` is easy: you can simply setup the `Traktor` 
default music directories to include `Beets`' folder. 

The issue is rather importing `Traktor`'s library in `Beets`:
- if you copy the files in `Beets`, you'd end up with useless duplicates
- if you move the files to `Beets`, you'd need to relocate all the tracks
- running `beet import` is not easy if the files in your `Traktor` library are not centralized

That's why I implemented some utils for this use case

#### How these utils work

Let's see what happens step by step when running `pipenv run import` 
(this also happens when running `pipenv run sync`):
0. Import whatever you want in `Traktor`, you can also sort your tracks in playlists like explained above: 
this will be tagged later even if your tracks are not imported in `beets` yet
1. _Automatic_: find all tracks imported in `Traktor` but not in `Beets`
2. _Automatic_: symlink these files to a temporary directory organized by album 
3. _Manual action required_: `beet import` in the temporary directory. 
**Warning:** you need to 
[configure](https://beets.readthedocs.io/en/stable/reference/config.html#link) 
`import.link = yes` in `Beets` config 
4. _Manual action required_: **close Traktor if opened**.
5. At this point, we have a double symlink: `beet_library -> temporary folder -> original track`
6. _Automatic_: detects that tracks have been imported in `Beets` thanks to the symlinks.
7. _Automatic_: delete symlinks, move the original files to `beet_library`, 
and update `Traktor` library to point to `beet_library` instead of the original files. 
8. You can reopen Traktor now :)
 

## Motivations

If you take a look at Native Instrument's forum, you'll find that a lot of people are frustrated 
by Traktor filesystem. So am I. I do love Traktor, but there are still some major painpoints:
- **Traktor doesn't handle custom metadata**. 
- **Traktor tends to get messy when sorting genres, artists etc.**


#### Frustrated by my previous workflow

My typical workflow is to sort tracks by `genre` and by `energy` (which I rate from 1 to 5).

Since Traktor doesn't handle custom metadata, I used to create a playlist for each energy level.

But then the playlists were messy: they included a whole bunch of different genres, 
and genres are annoying to filter in Traktor.
So I started creating playlists with `genre + energy` (example: `disco energy 5`, `house energy 3`...)

However this started to become very frustrating for multiple reasons:
- I wanted to add new tags, like the `mood` of a song (example: `joyful`, `dark` etc.)
But then I'd need to move tracks between playlists, and since playlists are not synced, creating something
like `genre: techno mood: joyful` + `genre: techno mood:dark` requires too much work
- As a software engineer, I like clean data storage: replacing metadata by a hacky playlist system 
is just not a satisfying way to handle this issue on the long term. 
I prefer organizing my library independently of the DJ Software I'm using, this is more robust.

And then I discovered [Beets](https://github.com/beetbox/beets), and it solved all more problems. 

#### Why use beets

`Beets` is a great open-source music library management software. Some main beets features:
- it helps you tag your songs by identifying your songs on online databases
- it centralizes your music files in one folder and it automatically keeps it organized
- it has great support for custom tags, and helps you list/modify tags easily through a CLI (`beet ls`, `beet modify`)
- it has a whole bunch of cool plugins (like the `smart playlists` plugin that automatically 
generates `m3u` playlists by filtering metadata)
- you can easily write your own code to interact with `Beets` (like I did) 

However, using `Beets` + `Traktor` was not always easy:
- you need to migrate your library from `Traktor` to `Beets`. 
Since it's best to move files to beets' centralized folder, you need to relocate all files in your 
Traktor library so that they point to the `Beets` folder
- using `Beets`'s metadata in `Traktor` is easy (you can simply generate `smart playlists`), 
but there was no support for the `Traktor` -> `Beets` export: 
say I want to rate a song 5 stars in Traktor, how do I write this metadata in `Beets` ?
- without a project like this one, when adding new tracks, 
you need to first import them in `Beets` before using them in `Traktor`, which is extremely annoying. 

So that's how I decided to code this project, it solves these issues by providing 
a decent sync between `Beets` and `Traktor`, so that you can do most of your library management in `Traktor`,
and worry about `Beets` later.
