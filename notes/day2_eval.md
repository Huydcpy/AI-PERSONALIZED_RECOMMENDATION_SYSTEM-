# Day 2: feature audit and qualitative evaluation

Executed on MovieLens 100K using train-only profiles. No rating or ranking metrics are claimed.

## Feature audit

- Movies: 1682; all 19 binary genre columns are present.
- Unknown ratio: 0.1189%.
- Features: 18 known genres; unknown is excluded; vectors and profiles use L2 normalization.

| Genre | Movies |
|---|---:|
| drama | 725 |
| comedy | 505 |
| action | 251 |
| thriller | 251 |
| romance | 247 |
| adventure | 135 |
| children | 122 |
| crime | 109 |
| sci_fi | 101 |
| horror | 92 |
| war | 71 |
| mystery | 61 |
| musical | 56 |
| documentary | 50 |
| animation | 42 |
| western | 27 |
| film_noir | 24 |
| fantasy | 22 |
| unknown | 2 |

Zero-known-genre movies: 267 (unknown), 1373 (Good Morning (1971)).

## User recommendations

### User 1

| ID | Title | Score | Reason |
|---|---|---:|---|
| 47 | Ed Wood (1994) | 0.854346 | Khớp thể loại: Comedy, Drama |
| 65 | What's Eating Gilbert Grape (1993) | 0.854346 | Khớp thể loại: Comedy, Drama |
| 150 | Swingers (1996) | 0.854346 | Khớp thể loại: Comedy, Drama |
| 236 | Citizen Ruth (1996) | 0.854346 | Khớp thể loại: Comedy, Drama |
| 316 | As Good As It Gets (1997) | 0.854346 | Khớp thể loại: Comedy, Drama |

### User 196

| ID | Title | Score | Reason |
|---|---|---:|---|
| 34 | Doom Generation, The (1995) | 0.913554 | Khớp thể loại: Comedy, Drama |
| 45 | Eat Drink Man Woman (1994) | 0.913554 | Khớp thể loại: Comedy, Drama |
| 47 | Ed Wood (1994) | 0.913554 | Khớp thể loại: Comedy, Drama |
| 65 | What's Eating Gilbert Grape (1993) | 0.913554 | Khớp thể loại: Comedy, Drama |
| 93 | Welcome to the Dollhouse (1995) | 0.913554 | Khớp thể loại: Comedy, Drama |

### User 405

| ID | Title | Score | Reason |
|---|---|---:|---|
| 74 | Faster Pussycat! Kill! Kill! (1965) | 0.838639 | Khớp thể loại: Action, Comedy, Drama |
| 34 | Doom Generation, The (1995) | 0.828180 | Khớp thể loại: Comedy, Drama |
| 93 | Welcome to the Dollhouse (1995) | 0.828180 | Khớp thể loại: Comedy, Drama |
| 150 | Swingers (1996) | 0.828180 | Khớp thể loại: Comedy, Drama |
| 236 | Citizen Ruth (1996) | 0.828180 | Khớp thể loại: Comedy, Drama |

## Similar movies

The task plan labels Pulp Fiction as ID 296; the actual MovieLens 100K ID is resolved from the exact title below.

### Toy Story (1995) - ID 1

Genres: animation, children, comedy

| ID | Title | Score | Reason |
|---|---|---:|---|
| 422 | Aladdin and the King of Thieves (1996) | 1.000000 | Cùng thể loại: Animation, Children, Comedy |
| 95 | Aladdin (1992) | 0.866025 | Cùng thể loại: Animation, Children, Comedy |
| 1219 | Goofy Movie, A (1995) | 0.866025 | Cùng thể loại: Animation, Children, Comedy |
| 63 | Santa Clause, The (1994) | 0.816497 | Cùng thể loại: Children, Comedy |
| 94 | Home Alone (1990) | 0.816497 | Cùng thể loại: Children, Comedy |

### Star Wars (1977) - ID 50

Genres: action, adventure, romance, sci_fi, war

| ID | Title | Score | Reason |
|---|---|---:|---|
| 181 | Return of the Jedi (1983) | 1.000000 | Cùng thể loại: Action, Adventure, Romance, Sci-Fi, War |
| 172 | Empire Strikes Back, The (1980) | 0.912871 | Cùng thể loại: Action, Adventure, Romance, Sci-Fi, War |
| 271 | Starship Troopers (1997) | 0.894427 | Cùng thể loại: Action, Adventure, Sci-Fi, War |
| 498 | African Queen, The (1951) | 0.894427 | Cùng thể loại: Action, Adventure, Romance, War |
| 62 | Stargate (1994) | 0.774597 | Cùng thể loại: Action, Adventure, Sci-Fi |

### Pulp Fiction (1994) - ID 56

Genres: crime, drama

| ID | Title | Score | Reason |
|---|---|---:|---|
| 76 | Carlito's Way (1993) | 1.000000 | Cùng thể loại: Crime, Drama |
| 182 | GoodFellas (1990) | 1.000000 | Cùng thể loại: Crime, Drama |
| 293 | Donnie Brasco (1997) | 1.000000 | Cùng thể loại: Crime, Drama |
| 346 | Jackie Brown (1997) | 1.000000 | Cùng thể loại: Crime, Drama |
| 504 | Bonnie and Clyde (1967) | 1.000000 | Cùng thể loại: Crime, Drama |

## Checks and limits

- Three users each returned 10 content-based results with no train-seen items.
- All similar results share at least one known genre and exclude the source movie.
- Unknown user 999999 and both zero-genre movies use Popularity with an explicit fallback reason.
- Three recommendation calls on an initialized service: 0.0142 seconds total on this machine.
- Genre-only vectors produce ties and repeated recommendations; movie_id breaks ties deterministically.
- Scores are cosine similarities, not predicted ratings. Popularity fallback uses its own rating score scale.
- Qualitative correctness does not demonstrate ranking quality; ranking metrics remain Day 3.
- Local tests: all 23 passed, including Surprise, after installing Microsoft C++ Build Tools and building scikit-surprise 1.1.4.
- Streamlit AppTest covered Home and all five pages, recommendations for three users, and similar movies for three titles.
