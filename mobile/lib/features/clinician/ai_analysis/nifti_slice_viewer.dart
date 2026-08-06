import 'dart:async';
import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:brainon_mobile/features/clinician/ai_analysis/clinician_ai_analysis_repository.dart';
import 'package:flutter/material.dart';

class NiftiSliceViewer extends StatefulWidget {
  const NiftiSliceViewer({
    required this.caseId,
    required this.repository,
    required this.initialSlice,
    super.key,
  });

  final String caseId;
  final ClinicianAiAnalysisRepository repository;
  final int? initialSlice;

  @override
  State<NiftiSliceViewer> createState() => _NiftiSliceViewerState();
}

class _NiftiSliceViewerState extends State<NiftiSliceViewer> {
  _NiftiVolume? _source;
  _NiftiVolume? _mask;
  ui.Image? _image;
  int _slice = 0;
  bool _maskVisible = true;
  double _maskOpacity = .55;
  Object? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final bytes = await Future.wait([
        widget.repository.fetchVolume(widget.caseId, 'source'),
        widget.repository.fetchVolume(widget.caseId, 'mask'),
      ]);
      final source = _NiftiVolume.parse(bytes[0]);
      final mask = _NiftiVolume.parse(bytes[1]);
      final requested = widget.initialSlice ?? source.depth ~/ 2;
      _source = source;
      _mask = mask;
      _slice = requested.clamp(0, source.depth - 1).toInt();
      await _render();
    } catch (error) {
      if (mounted) setState(() => _error = error);
    }
  }

  Future<void> _render() async {
    final source = _source;
    final mask = _mask;
    if (source == null || mask == null) return;
    final rgba = Uint8List(source.width * source.height * 4);
    final values = List<double>.generate(
      source.width * source.height,
      (index) => source.value(index, _slice),
      growable: false,
    );
    final sorted = [...values]..sort();
    final low = sorted[(sorted.length * .02).floor()];
    final high = sorted[(sorted.length * .98).floor()];
    final range = high > low ? high - low : 1.0;
    for (var index = 0; index < values.length; index++) {
      final gray = (((values[index] - low) / range).clamp(0, 1) * 255).round();
      final lesion = _maskVisible && mask.value(index, _slice) > .5;
      final offset = index * 4;
      if (lesion) {
        rgba[offset] = (gray * (1 - _maskOpacity) + 255 * _maskOpacity).round();
        rgba[offset + 1] = (gray * (1 - _maskOpacity)).round();
        rgba[offset + 2] = (gray * (1 - _maskOpacity)).round();
      } else {
        rgba[offset] = gray;
        rgba[offset + 1] = gray;
        rgba[offset + 2] = gray;
      }
      rgba[offset + 3] = 255;
    }
    final completer = Completer<ui.Image>();
    ui.decodeImageFromPixels(
      rgba,
      source.width,
      source.height,
      ui.PixelFormat.rgba8888,
      completer.complete,
    );
    final image = await completer.future;
    if (mounted) setState(() => _image = image);
  }

  @override
  Widget build(BuildContext context) {
    final source = _source;
    if (_error != null) {
      return Container(
        height: 260,
        color: Colors.black,
        alignment: Alignment.center,
        padding: const EdgeInsets.all(20),
        child: Text('CT 영상을 불러오지 못했습니다.\n$_error', textAlign: TextAlign.center, style: const TextStyle(color: Colors.white70)),
      );
    }
    if (source == null || _image == null) {
      return const SizedBox(height: 260, child: Center(child: CircularProgressIndicator()));
    }
    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        children: [
          Container(
            height: 320,
            width: double.infinity,
            color: Colors.black,
            child: InteractiveViewer(
              minScale: .5,
              maxScale: 6,
              child: Center(child: RawImage(image: _image, fit: BoxFit.contain)),
            ),
          ),
          Row(
            children: [
              IconButton(
                tooltip: 'AI 마스크 표시',
                onPressed: () async {
                  _maskVisible = !_maskVisible;
                  await _render();
                },
                icon: Icon(_maskVisible ? Icons.visibility : Icons.visibility_off),
              ),
              Expanded(
                child: Slider(
                  value: _slice.toDouble(),
                  min: 0,
                  max: (source.depth - 1).toDouble(),
                  divisions: source.depth > 1 ? source.depth - 1 : null,
                  label: '${_slice + 1}/${source.depth}',
                  onChanged: (value) async {
                    _slice = value.round();
                    await _render();
                  },
                ),
              ),
              Text('${_slice + 1}/${source.depth}  '),
            ],
          ),
          if (_maskVisible)
            Row(
              children: [
                const SizedBox(width: 16),
                const Text('마스크'),
                Expanded(
                  child: Slider(
                    value: _maskOpacity,
                    min: .1,
                    max: .9,
                    onChanged: (value) async {
                      _maskOpacity = value;
                      await _render();
                    },
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }
}

class _NiftiVolume {
  const _NiftiVolume(this.bytes, this.width, this.height, this.depth, this.datatype, this.offset, this.slope, this.intercept, this.endian);

  final ByteData bytes;
  final int width, height, depth, datatype, offset;
  final double slope, intercept;
  final Endian endian;

  factory _NiftiVolume.parse(Uint8List input) {
    final data = input.length > 2 && input[0] == 0x1f && input[1] == 0x8b
        ? Uint8List.fromList(gzip.decode(input))
        : input;
    if (data.length < 352) throw const FormatException('올바른 NIfTI 파일이 아닙니다.');
    final bytes = ByteData.sublistView(data);
    final little = bytes.getInt32(0, Endian.little) == 348;
    final endian = little ? Endian.little : Endian.big;
    if (bytes.getInt32(0, endian) != 348) throw const FormatException('지원하지 않는 NIfTI 헤더입니다.');
    final slopeValue = bytes.getFloat32(112, endian);
    return _NiftiVolume(
      bytes,
      bytes.getInt16(42, endian),
      bytes.getInt16(44, endian),
      bytes.getInt16(46, endian),
      bytes.getInt16(70, endian),
      bytes.getFloat32(108, endian).round(),
      slopeValue == 0 ? 1 : slopeValue,
      bytes.getFloat32(116, endian),
      endian,
    );
  }

  double value(int pixel, int slice) {
    final voxel = slice * width * height + pixel;
    final raw = switch (datatype) {
      2 => bytes.getUint8(offset + voxel),
      4 => bytes.getInt16(offset + voxel * 2, endian),
      8 => bytes.getInt32(offset + voxel * 4, endian),
      16 => bytes.getFloat32(offset + voxel * 4, endian),
      64 => bytes.getFloat64(offset + voxel * 8, endian),
      _ => throw FormatException('지원하지 않는 NIfTI datatype: $datatype'),
    };
    return raw.toDouble() * slope + intercept;
  }
}
