// Glass with fresnel reflection & transparency...
// Tested on: ATI Radeon Mobility

Shader "GooBall/Projection" { /*
	Properties {
		_ShadowTex ("shadow", 2D) = "fresnel.png" {
			TexGen ObjectLinear 	
		}
		_HiliteTex ("HiLite", 2D) = "fresnel.png" {
			TexGen ObjectLinear 	
		}
		_FalloffTex ("FallOff", 2D) = "fresnel.png" {
			TexGen ObjectLinear	
		}
		_CombineTex ("Hilite+shadow", 2D) = "fresnel.png" {
			TexGen ObjectLinear	
		}
	}

	Subshader { 
		Pass {
			ZWrite off
			Offset -3, -3

			Material {
				Diffuse (.5, .5, .5,1)
				Emission (.5,.5,.5,0)
			}
			Lighting On
			Fog {Color (.5, .5, .5) }
			AlphaTest Greater 0.01
			ColorMask RGB
			// Get fresnel value into alpha. This is used in next stage.
			Blend DstColor SrcColor
			SetTexture [_ShadowTex] { 
				constantColor (.5,.5,.5,.5)
				combine constant lerp (texture alpha) primary, one - texture
				Matrix [_Projector]
			}

			SetTexture [_HiliteTex] { 
				combine primary lerp (texture) one - previous, previous + texture
				Matrix [_Projector]
			}

			SetTexture [_FalloffTex] { 
				Matrix [_ProjectorClip]
				constantColor (.5,.5,.5,5)
				combine previous lerp (texture alpha) constant, previous
			}
		}
	}

	Subshader { 
		Pass {
			ZWrite off
			Offset -1, -3
			Lighting On
			Color (1,1,1)
			Material {
				Diffuse (.5, .5, .5,1)
				Emission (.5,.5,.5,0)
			}
			AlphaTest Greater 0.1
			ColorMask RGB
			// Get fresnel value into alpha. This is used in next stage.
			Blend DstColor SrcColor
			SetTexture [_CombineTex] { 
				Matrix [_Projector]
				combine texture lerp (previous alpha) previous, previous * texture alpha
			}
			SetTexture [_FalloffTex] { 
				Matrix [_ProjectorClip]
				constantColor (.5,.5,.5,5)
				combine previous lerp (texture alpha) constant, texture alpha
			}
		}
	}
	Properties {
		_ShadowTex ("Cookie", 2D) = "fresnel.png" {
			TexGen ObjectLinear 	
		}
		_FalloffTex ("FallOff", 2D) = "fresnel.png" {
			TexGen ObjectLinear	
		}
	}*/

	Properties {
		_ShadowTex ("shadow", 2D) = "fresnel.png" {
			TexGen ObjectLinear 	
		}
		_HiliteTex ("HiLite", 2D) = "fresnel.png" {
			TexGen ObjectLinear 	
		}
		_FalloffTex ("FallOff", 2D) = "fresnel.png" {
			TexGen ObjectLinear	
		}
		_CombineTex ("Hilite+shadow", 2D) = "fresnel.png" {
			TexGen ObjectLinear	
		}
	}

/*	Subshader {
		Pass {
			ZWrite off
			Offset -1, -1

			Fog { Color (1, 1, 1) }
			AlphaTest Greater 0
			ColorMask RGB
			Blend DstColor Zero
			SetTexture [_ShadowTex] {
				combine texture, ONE - texture
				Matrix [_Projector]
			}
			SetTexture [_FalloffTex] {
				constantColor (1,1,1,0)
				combine previous lerp (texture) constant
				Matrix [_ProjectorClip]
			}
		}
	}*/

/*	Subshader { 
		Pass {
			ZWrite off
			Offset -3, -3

			Material {
				Diffuse (.5, .5, .5,1)
				Emission (.5,.5,.5,0)
			}
			Lighting On
			Fog {Color (.5, .5, .5) }
			AlphaTest Greater 0.01
			ColorMask RGB
			// Get fresnel value into alpha. This is used in next stage.
			Blend DstColor SrcColor
			SetTexture [_ShadowTex] { 
				constantColor (.5,.5,.5,.5)
				combine constant lerp (texture alpha) primary, one - texture
				Matrix [_Projector]
			}

			SetTexture [_HiliteTex] { 
				combine primary lerp (texture) one - previous, previous + texture
				Matrix [_Projector]
			}

			SetTexture [_FalloffTex] { 
				Matrix [_ProjectorClip]
				constantColor (.5,.5,.5,5)
				combine previous lerp (texture alpha) constant, previous
			}
		}
	}
*/
	Subshader { 
		Pass {
			ZWrite off
			Offset -1, -3
			Lighting On
			Color (1,1,1)
			Material {
				Diffuse (.5, .5, .5,1)
				Emission (.5,.5,.5,0)
			}
			AlphaTest Greater 0.1
			ColorMask RGB
			// Get fresnel value into alpha. This is used in next stage.
			Blend DstColor SrcColor
			SetTexture [_CombineTex] { 
				Matrix [_Projector]
				combine texture lerp (previous alpha) previous, previous * texture alpha
			}
			SetTexture [_FalloffTex] { 
				Matrix [_ProjectorClip]
				constantColor (.5,.5,.5,5)
				combine previous lerp (texture alpha) constant, texture alpha
			}
		}
	}
}
