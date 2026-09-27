# Stage 06E publisher and checkpoint provenance decision — DRAFT

Status: **not signed; no-go remains in force until completed**. This document
is intended for protocol-owner review before the independent cohort is read.
It does not assert that model training and RAISE images are disjoint.

## Dataset access record

- Dataset: official RAISE-1k camera-native NEFs, source:
  https://loki.disi.unitn.it/RAISE/download.html.
- Official CSV-manifest ZIP SHA-256:
  `2bf21449ed458502c09407cd9260b5d91fe27e7bc9e98f33bd108bbd8e40f8dc`.
- Documented study use: non-commercial research and education, with citation
  of Dang-Nguyen et al., *RAISE — A Raw Images Dataset for Digital Image
  Forensics*, ACM MMSys 2015; do not redistribute original NEFs.
- Access form completion and acceptance record: **protocol owner to verify**.
- Observed local file times supplied by the protocol owner: all 1,000 NEFs
  span 2026-09-25 12:44:04–16:05:09 UTC; all 20 shard JSON receipts span
  2026-09-25 12:44:37–16:05:10 UTC. These establish a plausible **download
  window**, but file modification times do not independently prove the date
  of official access-form submission or acceptance of publisher terms.
- On-disk audit: 1,000 originals rehashed and decoded; six duplicate-source
  identities excluded, two dHash candidates reviewed as distinct scenes;
  994 eligible, including 150 allocated independent. The pinned audit CSV
  SHA-256 is `b33e76252c40c14416e8dfbe944404413cdd76e8d5696df566596ffa80335dec`.
  The eligible manifest SHA-256 is
  `a989e066ab5c66bec753719b3a3006c15a0635504f63977750a9192aa2995426`.

## Actual checkpoint exposure

| Component | Actual bytes used | Reported training provenance | Residual issue |
| --- | --- | --- | --- |
| DPIR colour DRUNet | SHA-256 `479abe3c5327dfd10ff54a80ec7d4098ca80752a5c9492cdff31cee430bec4b4` | BSD, Waterloo Exploration, DIV2K, Flickr2K reported by its authors | No exact photograph-level source manifest for these released bytes has been verified against all RAISE renders and derivatives. |
| FBCNN colour JPEG model | SHA-256 `8b0e4ef23d59cf7ac934a342cb31a17619e4fa4a0b3374a9d78c5174312387e8` | DIV2K/Flickr2K reported; pinned training configuration references their combined training set | A Flickr or resized/reposted RAISE photograph cannot be ruled out by the existing source screen. |
| Gradient inverse comparator | No learned checkpoint; gradient regularizer strength 0.01 | Fixed mathematical inverse selected on development data | No pretrained-photograph overlap; its choice is development-informed. |

The image-level audit screened RAISE against the 140 Stage 05 source
originals and screened duplicates within RAISE. It did **not** compare RAISE
against DRUNet/FBCNN training photographs. Negative exact hashes and a dHash
screen cannot prove absence of resized, cropped, edited or internet reposts.
The DiffPIR development candidate was not selected for confirmatory Stage 06;
its checkpoint is not part of this freeze.

## Proposed decision for protocol-owner review

Two admissible decisions remain:

1. **Proceed with documented residual risk:** carry the exact DRUNet/FBCNN
   bytes and the 994-source allowlist into a bounded independent study of
   source-disjoint RAISE images. Explicitly disclose that image-level
   independence from pretrained model training is **unverified**. Do not use
   language such as “guaranteed unseen by the priors,” and do not generalise
   the score to an unrepresented acquisition chain.
2. **No-go pending additional image-level evidence:** obtain the actual
   checkpoint training-image manifests or comparable verification, screen
   accessible training photos against RAISE derivatives, adjudicate matches,
   and revise eligibility *before* looking at related independent outcomes.

**Decision: PENDING.** Record the chosen option, decision date, protocol
owner, evidence/access limits and any added exclusions here. A signed copy
must be hashed into the real freeze bundle. A bare statement that no overlap
was found in the Stage 05 source screen is insufficient.

The detailed source citations and audit boundary are in
`docs/stage_06b_pretrained_checkpoint_provenance_2026-09-25.md` and
`docs/stage_06b_raise_integrity_and_overlap_review_2026-09-25.md`.
