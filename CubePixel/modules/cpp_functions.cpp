#include <vector>
#include <cmath>


struct GameEntity {
    int shape;
    float* vertices;
    float* uvs;
    bool transparent;
    bool solid;
};


class WordGeneratorCpp {

    public:
        std::vector<GameEntity> entity_data; 


        void combine_mesh(int* entities, int chunk_with, int* position, float* vertices, float* uvs, int* indices) {
            for (int i = 0; i < pow(chunk_with, 3); i++) {
                thread_function(i, entities, chunk_with, position, vertices, uvs, indices);
            }
        }


    private:
        void thread_function(int i, int* entities, int chunk_with, int* position, float* vertices, float* uvs, int* indices) {
            int x, y, z, entity_position[3], zero[3] = {0, 0, 0};

            GameEntity entity;

            x = i / chunk_with / chunk_with;
            y = i / chunk_with % chunk_with;
            z = i % chunk_with % chunk_with;

            entity_position[0] = x - (chunk_with - 1) / 2 + position[0];
            entity_position[1] = y - (chunk_with - 1) / 2 + position[1];
            entity_position[2] = z - (chunk_with - 1) / 2 + position[2];

            entity = entity_data[entities[i]];

            if (entity.shape == 0) {
                return;
            }

            translate(entity.vertices, entity.shape, entity_position, vertices, indices[i]);
            translate(entity.uvs, entity.shape, zero, uvs, indices[i]);
        }


        void translate(float* data, int shape, int* position, float* result, int a) {
            for (int i = 0; i < shape; i++){
                result[i*3 + a*3 + 0] = data[i*3 + 0] + position[0];
                result[i*3 + a*3 + 1] = data[i*3 + 1] + position[1];
                result[i*3 + a*3 + 2] = data[i*3 + 2] + position[2];
            }
        }
};
