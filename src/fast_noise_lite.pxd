cdef extern from "FastNoiseLite.h":
    ctypedef float FNLfloat

    ctypedef enum fnl_noise_type:
        FNL_NOISE_OPENSIMPLEX2,
        FNL_NOISE_OPENSIMPLEX2S,
        FNL_NOISE_CELLULAR,
        FNL_NOISE_PERLIN,
        FNL_NOISE_VALUE_CUBIC,
        FNL_NOISE_VALUE

    ctypedef enum fnl_rotation_type_3d:
        FNL_ROTATION_NONE,
        FNL_ROTATION_IMPROVE_XY_PLANES,
        FNL_ROTATION_IMPROVE_XZ_PLANES

    ctypedef enum fnl_fractal_type:
        FNL_FRACTAL_NONE,
        FNL_FRACTAL_FBM,
        FNL_FRACTAL_RIDGED,
        FNL_FRACTAL_PINGPONG,
        FNL_FRACTAL_DOMAIN_WARP_PROGRESSIVE,
        FNL_FRACTAL_DOMAIN_WARP_INDEPENDENT

    ctypedef enum fnl_cellular_distance_func:
        FNL_CELLULAR_DISTANCE_EUCLIDEAN,
        FNL_CELLULAR_DISTANCE_EUCLIDEANSQ,
        FNL_CELLULAR_DISTANCE_MANHATTAN,
        FNL_CELLULAR_DISTANCE_HYBRID

    ctypedef enum fnl_cellular_return_type:
        FNL_CELLULAR_RETURN_TYPE_CELLVALUE,
        FNL_CELLULAR_RETURN_TYPE_DISTANCE,
        FNL_CELLULAR_RETURN_TYPE_DISTANCE2,
        FNL_CELLULAR_RETURN_TYPE_DISTANCE2ADD,
        FNL_CELLULAR_RETURN_TYPE_DISTANCE2SUB,
        FNL_CELLULAR_RETURN_TYPE_DISTANCE2MUL,
        FNL_CELLULAR_RETURN_TYPE_DISTANCE2DIV,

    ctypedef enum fnl_domain_warp_type:
        FNL_DOMAIN_WARP_OPENSIMPLEX2,
        FNL_DOMAIN_WARP_OPENSIMPLEX2_REDUCED,
        FNL_DOMAIN_WARP_BASICGRID

    cdef struct fnl_state:
        int seed
        float frequency
        fnl_noise_type noise_type
        fnl_rotation_type_3d rotation_type_3d
        fnl_fractal_type fractal_type
        int octaves
        float lacunarity
        float gain
        float weighted_strength
        float ping_pong_strength
        fnl_cellular_distance_func cellular_distance_func
        fnl_cellular_return_type cellular_return_type
        float cellular_jitter_mod
        fnl_domain_warp_type domain_warp_type
        float domain_warp_amp

    fnl_state fnlCreateState()

    float fnlGetNoise2D(fnl_state *state, FNLfloat x, FNLfloat y)

    float fnlGetNoise3D(fnl_state *state, FNLfloat x, FNLfloat y, FNLfloat z)

    void fnlDomainWarp2D(fnl_state *state, FNLfloat *x, FNLfloat *y)

    void fnlDomainWarp3D(fnl_state *state, FNLfloat *x, FNLfloat *y, FNLfloat *z)
