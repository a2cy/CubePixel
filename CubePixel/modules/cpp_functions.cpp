#include <iostream>
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


    bool check_occlusion(ushort chunk_size, int* position, ushort* entities, long* neighbor_chunks)
    {
        int x_position, y_position, z_position;
        ushort* neighbor_chunk;

        GameEntity neighbor;

        for (uint i = 0; i < (3 * 2); i++)
        {
            x_position = (i + 0) % 3 / 2 * (i / 3 * 2 - 1) + position[0];
            y_position = (i + 1) % 3 / 2 * (i / 3 * 2 - 1) + position[1];
            z_position = (i + 2) % 3 / 2 * (i / 3 * 2 - 1) + position[2];

            if (x_position < 0)
            {
                neighbor_chunk = (ushort*)neighbor_chunks[2];

                if (neighbor_chunk)
                {
                    neighbor = entity_data[neighbor_chunk[(x_position + chunk_size) * chunk_size * chunk_size + y_position * chunk_size + z_position]];

                    if (neighbor.transparent == true)
                    {
                        return false;
                    }
                }

                continue;
            }

            if (x_position >= chunk_size)
            {
                neighbor_chunk = (ushort*)neighbor_chunks[5];

                if (neighbor_chunk)
                {
                    neighbor = entity_data[neighbor_chunk[(x_position - chunk_size) * chunk_size * chunk_size + y_position * chunk_size + z_position]];

                    if (neighbor.transparent == true)
                    {
                        return false;
                    }
                }

                continue;
            }

            if (y_position < 0)
            {
                neighbor_chunk = (ushort*)neighbor_chunks[1];

                if (neighbor_chunk)
                {
                    neighbor = entity_data[neighbor_chunk[x_position * chunk_size * chunk_size + (y_position + chunk_size) * chunk_size + z_position]];

                    if (neighbor.transparent == true)
                    {
                        return false;
                    }
                }

                continue;
            }

            if (y_position >= chunk_size)
            {
                neighbor_chunk = (ushort*)neighbor_chunks[4];

                if (neighbor_chunk)
                {
                    neighbor = entity_data[neighbor_chunk[x_position * chunk_size * chunk_size + (y_position - chunk_size) * chunk_size + z_position]];

                    if (neighbor.transparent == true)
                    {
                        return false;
                    }
                }

                continue;
            }

            if (z_position < 0)
            {
                neighbor_chunk = (ushort*)neighbor_chunks[0];

                if (neighbor_chunk)
                {
                    neighbor = entity_data[neighbor_chunk[x_position * chunk_size * chunk_size + y_position * chunk_size + (z_position + chunk_size)]];

                    if (neighbor.transparent == true)
                    {
                        return false;
                    }
                }

                continue;
            }

            if (z_position >= chunk_size)
            {
                neighbor_chunk = (ushort*)neighbor_chunks[3];

                if (neighbor_chunk)
                {
                    neighbor = entity_data[neighbor_chunk[x_position * chunk_size * chunk_size + y_position * chunk_size + (z_position - chunk_size)]];

                    if (neighbor.transparent == true)
                    {
                        return false;
                    }
                }

                continue;
            }

            neighbor = entity_data[entities[x_position * chunk_size * chunk_size + y_position * chunk_size + z_position]];

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
        entity_position[2] = i % chunk_size % chunk_size - (chunk_size - 1) / 2 + position[2];

        entity = entity_data[entities[i]];

        translate(entity.shape, indices[i], entity.vertices, entity_position, vertices);
        translate(entity.shape, indices[i], entity.uvs, zero, uvs);
    }
};
