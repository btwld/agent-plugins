import 'package:flutter/material.dart';
import 'package:mix/mix.dart';

const pageColor = Color(0xFF07070B);
const inkColor = Color(0xFFF5F5F7);

/// Paste this file into DartPad, then click the checkbox to toggle the spring.
void main() => runApp(const _DemoApp());

class _DemoApp extends StatelessWidget {
  const _DemoApp();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(
        useMaterial3: true,
      ).copyWith(scaffoldBackgroundColor: pageColor),
      home: const Scaffold(
        body: SafeArea(
          child: Center(
            child: Padding(padding: .all(24), child: SpringCheck()),
          ),
        ),
      ),
    );
  }
}

/// A checkbox with a spring fill and a matching animated strikethrough.
///
/// Hold to shrink the box; release to toggle it. Each style owns its animation,
/// so the fill can bounce while the tick and label fade independently.
class SpringCheck extends StatefulWidget {
  const SpringCheck({super.key});

  @override
  State<SpringCheck> createState() => _SpringCheckState();
}

class _SpringCheckState extends State<SpringCheck> {
  bool _on = false;

  @override
  Widget build(BuildContext context) {
    final row = FlexBoxStyler()
        .direction(.horizontal)
        .spacing(12)
        .crossAxisAlignment(.center)
        .mainAxisSize(.min)
        .paddingY(8);
    final checkbox = StackBoxStyler()
        .size(28, 28)
        .borderRounded(6)
        .clipBehavior(.antiAlias)
        .stackAlignment(.center)
        .onPressed(.scale(0.95))
        .animate(.easeOut(160.ms));
    final outline = BoxStyler()
        .size(28, 28)
        .borderRounded(6)
        .border(.color(inkColor).width(2))
        .wrap(.opacity(0.28))
        .onHovered(.new().wrap(.opacity(0.5)))
        .animate(.easeOut(120.ms));
    final fill = BoxStyler()
        .size(28, 28)
        .color(inkColor)
        .borderRounded(6)
        .scale(_on ? 1 : 0.01)
        .animate(.spring(280.ms, bounce: 0.22));
    final tick = IconStyler()
        .size(18)
        .color(pageColor)
        .wrap(.opacity(_on ? 1 : 0))
        .animate(.easeOut(140.ms, delay: 40.ms));
    final labelStack = StackBoxStyler().stackAlignment(.centerLeft);
    final label = TextStyler()
        .color(inkColor)
        .fontSize(18)
        .fontWeight(.w600)
        .wrap(.opacity(_on ? 0.42 : 1))
        .animate(.easeOut(220.ms));
    final strike = BoxStyler()
        .height(1.5)
        .color(inkColor)
        .borderRounded(2)
        .wrap(
          .align(
            alignment: const Alignment(-1, -0.08),
            widthFactor: 1,
          ).scale(_on ? 1 : 0.01, 1, alignment: .centerLeft),
        )
        .animate(.spring(240.ms, bounce: 0.06));

    return Semantics(
      label: 'Ship the build',
      checked: _on,
      child: Pressable(
        key: const Key('spring-check'),
        onPress: () => setState(() => _on = !_on),
        child: row(
          children: [
            checkbox(
              children: [
                outline(),
                fill(key: const Key('spring-check-fill')),
                tick(icon: Icons.check_rounded),
              ],
            ),
            labelStack(
              children: [
                label('Ship the build'),
                Positioned.fill(child: strike()),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
