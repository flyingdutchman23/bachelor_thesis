cmake_minimum_required(VERSION 3.3)
project(launcher)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x -pthread")

set(SOURCE_FILES_LAUNCHER
    easylogging++.h
    GeometryHelper.cpp
    GeometryHelper.hpp
    Globals.cpp
    Globals.hpp
    Launcher.cpp
    Launcher.hpp
    main.cpp
    Ray.cpp
    Ray.hpp
    Vector.hpp
    Vector.tcc
    IOHelper.cpp
    IOHelper.hpp)

set(SOURCE_FILES_EDGES
    mainEdges.cpp
    GeometryHelper.hpp
    GeometryHelper.cpp
    Globals.hpp
    Globals.cpp
    Vector.hpp
    Vector.tcc
    IOHelper.hpp
    IOHelper.cpp)

add_executable(launcher ${SOURCE_FILES_LAUNCHER})
add_executable(edges ${SOURCE_FILES_EDGES})