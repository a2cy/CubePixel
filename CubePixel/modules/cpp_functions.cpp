#include <vector>
#include <cmath>


struct GameEntity
{
    uint shape;
    float* vertices;
    float* uvs;
    bool transparent;
    bool solid;
};


class WorldGeneratorCpp
{

    public:

    std::vector<GameEntity> entity_data; 


    void combine_mesh(ushort chunk_size, ushort* entities, int* position, float* vertices, float* uvs, int* indices)
    {
        for (uint i = 0; i < pow(chunk_size, 3); i++)
        {
            add_entity(i, chunk_size, entities, position, vertices, uvs, indices);
            }
    }


    bool check_occlusion(ushort chunk_size, int* position, ushort* entities)
    {
        int neighbor_position[3], offset, index;

        GameEntity neighbor;

        for (uint i = 0; i < 2 * 3; i++)
        {
            offset = i % 2 * 2 - 1;
            index = i / 2;

            neighbor_position[0] = position[0];
            neighbor_position[1] = position[1];
            neighbor_position[2] = position[2];

            neighbor_position[index] += offset;

            if (neighbor_position[0] < 0 or neighbor_position[0] >= chunk_size or
                neighbor_position[1] < 0 or neighbor_position[1] >= chunk_size or
                neighbor_position[2] < 0 or neighbor_position[2] >= chunk_size)
            {
                return false;
            }

            neighbor = entity_data[entities[neighbor_position[0] * chunk_size * chunk_size + neighbor_position[1] * chunk_size + neighbor_position[2]]];

            if (neighbor.transparent == true)
            {
                return false;
            }
        }

        return true;
    }


    private:

    void translate(uint shape, uint index, float* data, int* position, float* result)
        {
            for (uint i = 0; i < shape; i++)
            {
                result[i*3 + index*3 + 0] = data[i*3 + 0] + position[0];
                result[i*3 + index*3 + 1] = data[i*3 + 1] + position[1];
                result[i*3 + index*3 + 2] = data[i*3 + 2] + position[2];
            }
        }


    void add_entity(uint i, ushort chunk_size, ushort* entities, int* position, float* vertices, float* uvs, int* indices)
    {
        if (indices[i] == -1)
        {
            return;
        }

        int entity_position[3], zero[3] = {0, 0, 0};

        GameEntity entity;

        entity_position[0] = i / chunk_size / chunk_size - (chunk_size - 1) / 2 + position[0];
        entity_position[1] = i / chunk_size % chunk_size - (chunk_size - 1) / 2 + position[1];
        entity_position[2] = i % chunk_size - (chunk_size - 1) / 2 + position[2];

        entity = entity_data[entities[i]];

        translate(entity.shape, indices[i], entity.vertices, entity_position, vertices);
        translate(entity.shape, indices[i], entity.uvs, zero, uvs);
    }
};
