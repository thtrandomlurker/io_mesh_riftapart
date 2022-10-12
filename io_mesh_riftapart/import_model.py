import bpy
import bmesh
import os
import io
import struct

# Define some things for easier reading
# All of these were found by doesthisusername, don't forget to credit him
DICT = 51707972
ZONE_SCENE_OBJECTS = 111921842
MODEL_LOOK = 116096764
MODEL_INDEX = 140084797
ZONE_ACTOR_GROUPS = 217418350
ACTOR_PRIUS_BUILT = 324547272
MODEL_JOINT = 366976315
MODEL_TEX_VERT = 385071640
LEVEL_LINK_NAMES = 574014586
MODEL_BUILT = 675087235
LEVEL_ZONE_NAMES = 732116738
CONDUIT_ASSET_REFS = 792745678
ZONE_ASSET_REFERENCES = 819649033
MODEL_MATERIAL = 844151680
LEVEL_SOME_DATA = 865900302
ACTOR_OBJECT_BUILT = 910847100
LEVEL_REGIONS_BUILT = 963613720
LEVEL_REGION_NAMES = 1093720323
CONFIG_TYPE = 1242726946
MODEL_PARENT_IDS = 1255696229
LEVEL_ZONES_BUILT = 1308768096
MODEL_POLYELEMENT = 1407861363
CONFIG_ASSET_REFS = 1488475530
ZONE_SCRIPT_ACTIONS = 1582607567
ZONE_DECAL_GEOMETRY = 1702171323
ZONE_MODEL_INSTS = 1770516850
MODEL_TEX_VERT_SHORT = 1803902701
ZONE_ACTORS = 1885875384
MODEL_LOCATOR_LOOKUP = 1931263022
MODEL_SUBSET = 2027539422
LEVEL_BUILT = 2091329149
LIGHT_GRID_PROBES = 2530704317
LIGHT_GRID_DATA = 2575940425
MODEL_LOCATOR = 2673954731
ANIM_CLIP_DATA = 2681314336
MODEL_STD_VERT = 2844518043
ANIM_CLIP_LOOKUP = 3080516055
ZONE_SCRIPT_PLUGS = 3198898919
MODEL_MIRROR_IDS = 3308604256
MODEL_SKIN_BATCH = 3323666421
ZONE_MODEL_NAMES = 3332739166
CONDUIT_BUILT = 3467841128
ZONE_SCRIPT_VARS = 3630856500
ZONE_ACTOR_NAMES = 3697433405
MODEL_SKIN_DATA = 3701701026
MODEL_SKIN_BIND = 3704130073
CONFIG_BUILT = 3842054255
MODEL_JOINT_LOOKUP = 3996227356
ZONE_SCRIPT_STRINGS = 4018550741
MODEL_PHYSICS_DATA = 4023987816

def ReadStringAtOffset(off, f):
    print(off)
    pre = f.tell()
    f.seek(off)
    s = b""
    while True:
        b = f.read(1)
        if b != b"\x00":
            s += b
        else:
            ret = s.decode("ASCII")
            f.seek(pre)
            return ret

## FINALLY WORKING NORMALSSSSSSSSS
def UnpackNormals(n):
    bits = format(n, 'b').zfill(32)
    nZ = int(bits[1:12], 2)
    nY = int(bits[12:22], 2)
    nX = int(bits[22:32], 2)
    nX = (nX / 511.0) * 2 - 2
    nY = (nY / 511.0) * 2 - 2
    nZ = (nZ / 511.0) * 2 - 2
    return (nX, -nZ, nY)  # swap to X-ZY for Z UP

class Vertex:
    def __init__(self):
        self.Position = (0, 0, 0)
        self.Normal = (0, 0, 0)
        self.Tangent = (0, 0, 0)
    def Read(self, f):
        print(f.tell())
        tPos = struct.unpack("<hhh", f.read(6))
        f.seek(2, 1)  # we don't need the w
        self.Position = (tPos[0] / 4096, -(tPos[2] / 4096), tPos[1] / 4096)  # Flip to Z Up
        self.Normal = UnpackNormals(struct.unpack("<I", f.read(4))[0])
        if self.Position[1] < 0:
            self.Normal = (self.Normal[0], self.Normal[1] * -1, self.Normal[2])
        f.seek(4, 1)  # the rest is tangents. blender can't hold tangents.

class ModelSubset:
    def __init__(self):
        self.Vertices = []
        self.UVs = []
        self.Faces = []
        self.BindIndices = []
        self.BindWeights = []
        self.MaterialIndex = -1
    def Read(self, f, STDVertsOffset, TEXVertsOffset, IndexOffset, SkinBatchOffset, SkinDataOffset):
        SubsetUnks = f.read(12)
        ExtraUnks = f.read(8)
        StartVert = struct.unpack("<I", f.read(4))[0]
        StartIndex = struct.unpack("<I", f.read(4))[0]
        IndexCount = struct.unpack("<I", f.read(4))[0]
        VertCount = struct.unpack("<H", f.read(2))[0]
        Unk01 = struct.unpack("<H", f.read(2))[0]
        Flags = struct.unpack("<H", f.read(2))[0]
        self.MaterialIndex = struct.unpack("<H", f.read(2))[0]
        BindTableStartIdx = struct.unpack("<H", f.read(2))[0]
        BindTableCount = struct.unpack("<H", f.read(2))[0]
        Unk02 = struct.unpack("<H", f.read(2))[0]
        Unk03 = f.read(1)[0]
        VertInfoTableCount = f.read(1)[0]
        SubsetUnks2 = f.read(16)
        pre = f.tell()
        f.seek(STDVertsOffset + (0x10 * StartVert))
        print(f.tell())
        for i in range(VertCount):
            v = Vertex()
            v.Read(f)
            self.Vertices.append(v)
        f.seek(TEXVertsOffset + (0x04 * StartVert))
        for i in range(VertCount):
            tuv = struct.unpack("<hh", f.read(4))
            self.UVs.append((tuv[0] / 0x4000, -(tuv[1] / 0x4000)))
        f.seek(IndexOffset + (0x02 * StartIndex))
        for i in range(IndexCount//3):
            indices = struct.unpack("<hhh", f.read(6))
            if Flags & 0x10:
                self.Faces.append(indices)
            else:
                self.Faces.append((indices[0] - StartVert, indices[1] - StartVert, indices[2] - StartVert))
        #f.seek(SkinBatchOffset + (0x10 * BindTableStartIdx))
        #for i in range(BindTableCount):
        #    BindDataSetOffset = struct.unpack("<I", f.read(4))[0] + SkinDataOffset
        #    f.seek(0x06, 1)
        #    BonesPerVertex = struct.unpack("<H", f.read(2))[0]
        #    VertexCount = struct.unpack("<H", f.read(2))[0]
        #    VertexStartIndex = struct.unpack("<H", f.read(2))[0]
        #    ret = f.tell()
        #    f.seek(BindDataSetOffset)
        #    if BonesPerVertex == 0:
        #        for v in range(VertexCount):
        #            self.BindIndices.append([f.read(1)[0]])
        #            self.BindWeights.append([1.0])
        #    elif BonesPerVertex == 1:
        #        for v in range(VertexCount):
        #            b1 = f.read(1)[0]
        #            b2 = f.read(1)[0]
        #            w1 = f.read(1)[0] / 256
        #            w2 = f.read(1)[0] / 256
        #            self.BindIndices.append([b1, b2])
        #            self.BindWeights.append([w1, w2])
        #    elif BonesPerVertex == 2:
        #        for v in range(VertexCount):
        #            b1 = f.read(1)[0]
        #            b2 = f.read(1)[0]
        #            b3 = f.read(1)[0]
        #            b4 = f.read(1)[0]
        #            w1 = f.read(1)[0] / 256
        #            w2 = f.read(1)[0] / 256
        #            w3 = f.read(1)[0] / 256
        #            w4 = f.read(1)[0] / 256
        #            self.BindIndices.append([b1, b2, b3, b4])
        #            self.BindWeights.append([w1, w2, w3, w4])
        #    elif BonesPerVertex == 3:
        #        for v in range(VertexCount):
        #            b1 = f.read(1)[0]
        #            b2 = f.read(1)[0]
        #            b3 = f.read(1)[0]
        #            b4 = f.read(1)[0]
        #            b5 = f.read(1)[0]
        #            b6 = f.read(1)[0]
        #            b7 = f.read(1)[0]
        #            b8 = f.read(1)[0]
        #            w1 = f.read(1)[0] / 256
        #            w2 = f.read(1)[0] / 256
        #            w3 = f.read(1)[0] / 256
        #            w4 = f.read(1)[0] / 256
        #            w5 = f.read(1)[0] / 256
        #            w6 = f.read(1)[0] / 256
        #            w7 = f.read(1)[0] / 256
        #            w8 = f.read(1)[0] / 256
        #            self.BindIndices.append([b1, b2, b3, b4, b5, b6, b7, b8])
        #            self.BindWeights.append([w1, w2, w3, w4, w5, w6, w7, w8])
        #    f.seek(ret)
        f.seek(pre)

class JointInfo:
    def __init__(self):
        self.Parent = -1
        self.Sibling = -1
        self.Child = -1
        self.TransformLock = 0
        self.NameHash = -1
        self.BoneName = ""

    def Read(self, f):
        self.Parent = struct.unpack("<h", f.read(2))[0]
        self.Sibling = struct.unpack("<h", f.read(2))[0]
        self.Child = struct.unpack("<h", f.read(2))[0]
        self.TransformLocks = struct.unpack("<h", f.read(2))[0]
        self.NameHash = struct.unpack("<I", f.read(4))[0]
        self.BoneName = ReadStringAtOffset(struct.unpack("<I", f.read(4))[0], f)
        print(self.BoneName)

class Model:
    def __init__(self, f):
        self.Meshes = []
        self.Materials = []
        self.Joints = []  # temp. we just want to get the bone names
        self.BindPose = []  # list of the matrices that create the bind pose
        self.Read(f)
        
    def Read(self, f):
        Magic = f.read(4)
        Type = struct.unpack("<I", f.read(4))[0]
        print(hex(Type))
        if Type != 0x882A03DC and Type != 0xB0519752:
            raise Exception("Invalid file: Not a model.")
        FileSize = struct.unpack("<I", f.read(4))[0]
        SectionCount = struct.unpack("<I", f.read(4))[0]
        # Set some things up for later
        STDVertsOffset = 0
        STDVertsSize = 0
        TEXVertsOffset = 0
        TEXVertsSize = 0
        IndexOffset = 0
        IndexSize = 0
        SubsetOffset = 0
        SubsetSize = 0
        SkinDataOffset = 0
        SkinDataSize = 0
        SkinBatchOffset = 0
        SkinBatchSize = 0
        PolyElementOffset = 0
        PolyElementSize = 0
        JointInfoOffset = 0
        JointInfoSize = 0
        MaterialInfoOffset = 0
        MaterialInfoSize = 0
        BindPoseOffset = 0
        BindPoseSize = 0
        for i in range(SectionCount):
            SectionType = struct.unpack("<I", f.read(4))[0]
            print(SectionType)
            if SectionType == MODEL_SUBSET:
                SubsetOffset = struct.unpack("<I", f.read(4))[0]
                SubsetSize = struct.unpack("<I", f.read(4))[0]
            elif SectionType == MODEL_STD_VERT:
                STDVertsOffset = struct.unpack("<I", f.read(4))[0]
                STDVertsSize = struct.unpack("<I", f.read(4))[0]
            elif SectionType == MODEL_TEX_VERT_SHORT:
                TEXVertsOffset = struct.unpack("<I", f.read(4))[0]
                TEXVertsSize = struct.unpack("<I", f.read(4))[0]
            elif SectionType == MODEL_INDEX:
                IndexOffset = struct.unpack("<I", f.read(4))[0]
                IndexSize = struct.unpack("<I", f.read(4))[0]
            elif SectionType == MODEL_SKIN_DATA:
                SkinDataOffset = struct.unpack("<I", f.read(4))[0]
                SkinDataSize = struct.unpack("<I", f.read(4))[0]
            elif SectionType == MODEL_POLYELEMENT:
                PolyElementOffset = struct.unpack("<I", f.read(4))[0]
                PolyElementSize = struct.unpack("<I", f.read(4))[0]
            #elif SectionType == MODEL_SKIN_BATCH:
            #    SkinBatchOffset = struct.unpack("<I", f.read(4))[0]
            #    SkinBatchSize = struct.unpack("<I", f.read(4))[0]
            elif SectionType == MODEL_JOINT:
                JointInfoOffset = struct.unpack("<I", f.read(4))[0]
                JointInfoSize = struct.unpack("<I", f.read(4))[0]
            elif SectionType == MODEL_MATERIAL:
                MaterialInfoOffset = struct.unpack("<I", f.read(4))[0]
                MaterialInfoSize = struct.unpack("<I", f.read(4))[0]
            elif SectionType == MODEL_SKIN_BIND:
                BindPoseOffset = struct.unpack("<I", f.read(4))[0]
                BindPoseSize = struct.unpack("<I", f.read(4))[0]
            else:
                f.seek(8, 1)
        #if MaterialInfoOffset != 0:  # has materials. should also always execute in theory
        #    f.seek(MaterialInfoOffset)
        #    while f.tell() < MaterialInfoOffset + MaterialInfoSize:
        #        MaterialFilePath = ReadStringAtOffset(struct.unpack("<Q", f.read(8))[0], f)
        #        MaterialName = ReadStringAtOffset(struct.unpack("<Q", f.read(8))[0], f)
        #        self.Materials.append(MaterialName)  # temporary. figure out materials proper and load them correctly later
        if SubsetOffset != 0:  # has subsets. Should always execute
            f.seek(SubsetOffset)
            while f.tell() < SubsetOffset + SubsetSize:
                Mesh = ModelSubset()
                Mesh.Read(f, STDVertsOffset, TEXVertsOffset, IndexOffset, SkinBatchOffset, SkinDataOffset)
                self.Meshes.append(Mesh)
        if JointInfoOffset != 0:  # get joint info for skinning data
            f.seek(JointInfoOffset)
            while f.tell() < JointInfoOffset + JointInfoSize:
                jnt = JointInfo()
                jnt.Read(f)
                self.Joints.append(jnt)
        #if BindPoseOffset != 0:  # has bone matrices. read and make bones. we skip because i have no clue how to make this functional
        #    f.seek(BindPoseOffset)
        #    for i in range(len(self.Joints)):  # because the size of the bind pose includes other data. likely inverse bind pose matrices.
        #        scale = struct.unpack("<ffff", f.read(16))
        #        rot = struct.unpack("<ffff", f.read(16))
        #        pos = struct.unpack("<ffff", f.read(16))
        #        nPos = pos
        #        if self.Joints[i].Parent != -1:
        #            nPos = [pos[0] + self.BindPose[self.Joints[i].Parent][2][0], pos[1] + self.BindPose[self.Joints[i].Parent][2][1], pos[2] + self.BindPose[self.Joints[i].Parent][2][2], pos[3] + self.BindPose[self.Joints[i].Parent][2][3]]
        #        self.BindPose.append([scale, rot, nPos])


def ReadModelFile(context, filepath):
    with open(filepath, 'rb') as f:
        # removed compression check code since game contents are seemingly entirely uncompressed
        f.seek(0)
        mdlDat = Model(f)
        for idx, Mesh in enumerate(mdlDat.Meshes):
            mesh = bpy.data.meshes.new(f"{os.path.split(filepath)[1].split('.')[0]}-subset{idx}")
            # check for material. make if it doesn't exist.
            #mat = bpy.data.materials.get(mdlDat.Materials[Mesh.MaterialIndex])
            #if mat == None:
            #    mat = bpy.data.materials.new(name=mdlDat.Materials[Mesh.MaterialIndex])
            #mesh.materials.append(mat)  # add the mat to the mesh
            bm = bmesh.new()
            uv = bm.loops.layers.uv.new()  # init the uv map
            Normals = []
            for Vertex in Mesh.Vertices:
                v = bm.verts.new(Vertex.Position)
                Normals.append((Vertex.Normal[0], Vertex.Normal[1], Vertex.Normal[2]))
            # ensure lookup table
            bm.verts.ensure_lookup_table()
            bm.verts.index_update()
            for Face in Mesh.Faces:
                try:
                    face = bm.faces.new([bm.verts[Face[0]], bm.verts[Face[1]], bm.verts[Face[2]]])
                except:
                    continue
                else:
                    for loop in face.loops:
                        loop[uv].uv = Mesh.UVs[loop.vert.index]
                    face.smooth = True
                    #face.material_index = 0
            bm.to_mesh(mesh)
            bm.free()
            mesh.use_auto_smooth = True
            #mesh.normals_split_custom_set_from_vertices(Normals)
            obj = bpy.data.objects.new(f"{os.path.split(filepath)[1].split('.')[0]}-subset{idx}", mesh)
            # add vertex groups
            #for i in range(len(Mesh.BindIndices)):
            #    for idx, Bone in enumerate(Mesh.BindIndices[i]):
            #        group = obj.vertex_groups.get(mdlDat.Joints[Bone].BoneName)
            #        if group == None:
            #            group = obj.vertex_groups.new(name=mdlDat.Joints[Bone].BoneName)
            #        # now we have the group. add the vert
            #        group.add([i], Mesh.BindWeights[i][idx], 'ADD')
            bpy.context.scene.collection.objects.link(obj)

    return {'FINISHED'}
