Shader "RenderFX/AddGlow1" {
	Properties {
		_fade ("Fade value", range (0,1)) = .1
	}

	Category {
		Cull Off
		ZTest Always
		ZWrite Off 
		Blend AppSrcAdd AppDstAdd 
		// Ohh yes - we love new Radeons
		SubShader {
			Pass {
				SetTexture [SmallRenderTex] { combine texture * constant}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
			}
		}
		// Radeon 6000
		SubShader {
			Pass {
				SetTexture [SmallRenderTex] { combine texture * constant}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
			}
		}
		// Geforce 3,4, TI on Mac
		SubShader {
			Pass {
				SetTexture [SmallRenderTex] { combine texture * constant}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
			}
		}
		// Radeon7k
		SubShader {
			Pass {
				SetTexture [SmallRenderTex] { combine texture * constant}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
			}
		}
		// Geforces 1,2, MX on Mac
		SubShader {
			Pass {
				SetTexture [SmallRenderTex] { combine texture * constant}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
			}
		}
		// Geforce 3, 4, FX
		SubShader {
			Pass {
Program "" {
SubProgram {
  Local 0, [_RTCol0]
  Local 1, [_RTCol1]
  Local 8, [_RTCol2]
  Local 16, [_RTCol3]

  "!!RC1.0
  {
    rgb
    {
      discard = const0.rgb * tex0.rgb;
      discard = const1.rgb * tex1.rgb;
      col0 = sum();
    }
  }
  {
    rgb
    {
      discard = col0.rgb * unsigned_invert(zero.rgb);
      discard = const0.rgb * tex2.rgb;
      col0 = sum();
    }
  }
  {
    rgb
    {
      discard = col0.rgb * unsigned_invert(zero.rgb);
      discard = const0.rgb * tex3.rgb;
      col0 = sum();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  	"
}
}
				SetTexture [SmallRenderTex] { combine texture * constant}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
				SetTexture [SmallRenderTex] { combine texture * constant + previous}
			}
		}
		// Geforce 1, 2, MX
		SubShader {
			Pass {
Program "" {
SubProgram {
  Local 0, [_RTCol0]
  Local 1, [_RTCol1]

  "!!RC1.0
  {
    rgb
    {
      discard = const0.rgb * tex0.rgb;
      discard = const1.rgb * tex1.rgb;
      col0 = sum();
    }
  }
  out.rgb = unsigned(col0.rgb);
  out.a = unsigned(col0.a);
  	"
}
}
			}
		}
	}
}
 