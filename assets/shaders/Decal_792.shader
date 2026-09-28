Shader " Decal" {
	Properties {
		_Color ("Main Color", Color) = (1,1,1,1)
		_Shininess ("Shininess", range (0,1)) = 0.1
		_Highlight ("Highlight size", range (0,64)) = 30
		_MainTex2 ("Base (RGB)", Cube) = "ah64rotor1" {TexGen CubeReflect }
		_DecalTex ("Decal (RGBA)", 2D) = "ah64rotor1"
		_2D ("Base (RGB)", 2D) = "ah64rotor1" {TexGen SphereMap }
	}

	Category {
		SubShader {
			Material {
				Diffuse [_Color]
				Specular ([_Shininess], [_Shininess], [_Shininess], 0)
				Shininess [_Highlight]
			}
			Pass {
				Lighting On
				SeperateSpecular On
				SetTexture [_MainTex2] {Combine texture}
				SetTexture [_DecalTex] {Combine texture lerp (texture) previous}
				SetTexture [_MainTex2] {Combine previous * primary DOUBLE, previous * constant constantColor [_Color]}
			}
		}
	}
	Category {
		SubShader {
			Material {
				Diffuse [_Color]
				Specular ([_Shininess], [_Shininess], [_Shininess], 0)
				Shininess [_Highlight]
			}
			Pass {
				Lighting On
				SetTexture [_2D] {Combine texture}
				SetTexture [_DecalTex] {Combine texture lerp (texture) previous}
			}
		}
	}
}
