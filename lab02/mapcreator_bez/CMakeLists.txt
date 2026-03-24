cmake_minimum_required(VERSION 3.14)
set(CMAKE_POLICY_DEFAULT_CMP0000 NEW)
set(CMAKE_POLICY_VERSION_MINIMUM 3.5)

project(MapCreator_NoPattern)

set(CMAKE_CXX_STANDARD 17)

# Путь к  распакованной SFML 
set(SFML_DIR "${CMAKE_SOURCE_DIR}/external/SFML-2.6.1/lib/cmake/SFML")
find_package(SFML 2.6 COMPONENTS graphics window system REQUIRED)

# JSON 
include(FetchContent)
FetchContent_Declare(json URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz)
FetchContent_MakeAvailable(json)

add_executable(MapCreator_NoPattern src/main.cpp)
target_link_libraries(MapCreator_NoPattern PRIVATE sfml-graphics sfml-window sfml-system nlohmann_json::nlohmann_json)

# Копируем нужные .dll в папку с .exe, чтобы программа запустилась
add_custom_command(TARGET MapCreator_NoPattern POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    "${CMAKE_SOURCE_DIR}/external/SFML-2.6.1/bin"
    $<TARGET_FILE_DIR:MapCreator_NoPattern>
)
