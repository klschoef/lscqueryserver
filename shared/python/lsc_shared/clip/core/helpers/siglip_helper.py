import torch


def resolve_projection(model, kind="text"):
    projection_attr_candidates = (
        ["text_projection", "text_proj"] if kind == "text"
        else ["visual_projection", "vision_projection", "image_projection", "visual_proj", "vision_proj"]
    )
    for attr in projection_attr_candidates:
        proj = getattr(model, attr, None)
        if proj is not None:
            return proj
    return None


def maybe_project_tensor(model, features, kind="text"):
    if not isinstance(features, torch.Tensor):
        return features

    projection = resolve_projection(model, kind=kind)
    if projection is None:
        return features

    in_features = getattr(projection, "in_features", None)
    if in_features is not None:
        if features.shape[-1] == in_features:
            return projection(features)
        return features

    if isinstance(projection, torch.Tensor) and features.shape[-1] == projection.shape[0]:
        return features @ projection

    return features


def project_siglip_features(model, output_obj, kind="text"):
    if isinstance(output_obj, torch.Tensor):
        # get_text_features/get_image_features typically already return projected features.
        return output_obj

    embed_attr_candidates = (
        ["text_embeds", "embeds"] if kind == "text"
        else ["image_embeds", "embeds"]
    )
    for attr in embed_attr_candidates:
        embeds = getattr(output_obj, attr, None)
        if embeds is not None:
            # *_embeds fields are projected embeddings.
            return embeds

    pooled = getattr(output_obj, "pooler_output", None)
    if pooled is not None:
        return maybe_project_tensor(model, pooled, kind=kind)

    if isinstance(output_obj, (tuple, list)) and len(output_obj) > 0:
        return maybe_project_tensor(model, output_obj[0], kind=kind)

    raise TypeError(f"Unsupported SigLIP2 {kind} feature output type: {type(output_obj)}")
