# Utils to interact with openSCHEMA PostgreSQL Database

## Structure
``` text
.
├── CMakeLists.txt
├── app
│   └── main.cpp                <- Examples how to use the utils
├── include
│   ├── exampleConfig.h.in
│   └── postgres_utils.h        <- PostgreSQL Utils header
├── src
│   └── postgres_utils.cpp      <- PostgreSQL Utils implementation
└── tests
    ├── test_utils.cpp          <- [WIP] Unit- and integration tests
    └── main.cpp
```

Sources go in [src/](src/), header files in [include/](include/), main programs in [app/](app), and
tests go in [tests/](tests/) (compiled to `unit_tests` by default).

## Building

Build by making a build directory (i.e. `build/`), run `cmake` in that dir, and then use `make` to build the desired target.

Example:

``` bash
> mkdir build && cd build
> cmake .. -DCMAKE_BUILD_TYPE=[Debug | Coverage | Release]
> make
> ./main
> make test      # Makes and runs the tests.
> make coverage  # Generate a coverage report.
> make doc       # Generate html documentation.
```

## .gitignore

The [.gitignore](.gitignore) file is a copy of the [Github C++.gitignore file](https://github.com/github/gitignore/blob/master/C%2B%2B.gitignore),
with the addition of ignoring the build directory (`build/`).

