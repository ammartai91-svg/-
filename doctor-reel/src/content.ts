// ============================================================================
//  ملف المحتوى — كل شي بالفيديو يتعدّل من هنا
//  - النصوص، التوقيتات (بالثواني)، الألوان، مكان الدكتورة، الموسيقى والساوند
//  - تضيف نقطة: انسخ بلوك نقطة من points وغيّر النص والتوقيت
//  - تحذف نقطة: امسح البلوك مالها
//  - التوقيتات لازم تكون متسلسلة: كل نقطة تبدي بعد ما تخلص اللي قبلها
// ============================================================================

export type IconName = 'calendar' | 'apple' | 'pill' | 'alert' | 'heart' | 'stethoscope';

export type Point = {
  /** الرقم الكبير المفرّغ اللي يطلع ورا العنوان */
  number: string;
  /** الكلمة الكبيرة المتوهجة (سطر أو سطرين، افصل بـ \n) */
  title: string;
  /** السطر الصغير داخل الشريط الملوّن */
  subtitle: string;
  icon: IconName;
  /** وقت بداية النقطة بالثواني (من بداية الفيديو) */
  start: number;
  /** مدة النقطة بالثواني */
  duration: number;
  /** شريط بحث ينكتب بيه سؤال (اختياري) */
  search?: string;
  /** فلاش انعكاس الألوان (نفس الريفرنس) عند دخول النقطة */
  flash?: boolean;
  /** زوم الكاميرا على الدكتورة: 1 = عريض، 1.14 = قريب */
  zoom?: number;
  /** ثواني إضافية داخل النقطة يتبدل بيها الزوم (للنقاط الطويلة) */
  punch?: number[];
};

import edl from '../public/video/edl.json';

export const content = {
  fps: 30,
  width: 1080,
  height: 1920,

  // هوية حملة «نبض ينتظر قلبك»
  colors: {
    primary: '#FFFFFF', // أبيض — العناوين (على خلفية التركواز)
    glow: '#FF6B95', // وردي — التوهج
    accent: '#FF2D6F', // الشريط
    deep: '#14213A', // الخلفية الختامية
    text: '#14213A',
  },
  logo: 'logo.png' as string | null, // بمجلد public

  // ---------------------------------------------------------------- الدكتورة
  doctor: {
    // فيديو الدكتورة بمجلد public/video
    // doctor-tight.mp4 = فيديوها بعد شيل السكتات الطويلة (tools/tighten.py)
    src: 'video/doctor-tight.mp4' as string | null,
    // 'full' = فيديوها الأصلي بخلفيته | 'cutout' = مقصوصة داخل الغرفة البيضة
    mode: 'full' as 'full' | 'cutout',
    startFrom: 0, // من أي ثانية بالفيديو الأصلي نبدي
    clipDuration: edl.duration, // كم ثانية نستخدم من فيديوها
    delay: 0, // تأخير بداية كلامها (ثواني) — قبلها صورة ثابتة
    // إعدادات وضع cutout بس:
    x: -90,
    y: 0,
    height: 1380,
    mirror: false,
    volume: 1, // صوت الدكتورة
  },

  room: {
    enabled: false, // true يرجّع الغرفة البيضة (ويّا mode: 'cutout')
    image: null as string | null,
    showChair: true,
    showPlant: true,
  },

  // ---------------------------------------------------------------- الافتتاحية
  // أول ثانية بالفيديو هي سكتة قبل ما تحچي
  hook: {
    start: 0,
    duration: 1.4,
    ghost: '4',
    title: '٤ نصائح لصحّتج',
    subtitle: 'د. ابتسام صاحب • نسائية وتوليد',
  },

  // ---------------------------------------------------------------- النقاط
  // كل نقطة على لقطة من لقطات الفيديو (بعد شيل السكتات + ثانية الافتتاحية)
  points: [
    {
      number: '01',
      title: 'راجعي',
      subtitle: 'بصورة دورية',
      icon: 'calendar',
      start: 1.3,
      duration: 3.37,
      zoom: 1,
    },
    {
      number: '02',
      title: 'اهتمي بتغذيتج',
      subtitle: 'واسألي عن الفيتامينات المناسبة إلج',
      icon: 'apple',
      start: 4.67,
      duration: 5.57,
      search: 'شنو الفيتامينات المناسبة إلي؟',
      zoom: 1.14,
    },
    {
      number: '03',
      title: 'لا تاخذين',
      subtitle: 'أدوية أو مكملات من نفسج',
      icon: 'pill',
      start: 10.24,
      duration: 10.14,
      zoom: 1,
    },
    {
      number: '04',
      title: 'لا تهملين',
      subtitle: 'أي أعراض غير طبيعية',
      icon: 'alert',
      start: 20.38,
      duration: 5.24,
      zoom: 1.14,
    },
  ] as Point[],

  // أماكن القطع بعد شيل السكتات — الكاميرا تبدّل الزوم عليها حتى ما يبين القطع
  cuts: edl.cuts.map((t: number) => t + 0),

  // ---------------------------------------------------------------- الختام
  outro: {
    start: 25.62,
    duration: 3.3,
    brand: 'د. ابتسام\nصاحب',
    tagline: 'نبض ينتظر قلبك',
    phone: {label: 'للحجز', number: '0788 704 9494'} as {label: string; number: string} | null, // من ملف حملة نبض
    ghost: '', // كلمة إنكليزية عمودية مفرّغة على الموجة (فارغ = بدون)
    panX: 230, // قد إيش تتحرك الدكتورة لليسار حتى تفسح مجال للختام
  },

  // ---------------------------------------------------------------- الصوت
  audio: {
    music: 'music/bed.wav',
    // صوت الموسيقى لما الدكتورة تحچي (خفيف) ولما ماكو صوت
    musicVolumeUnderVoice: 0.14,
    musicVolumeAlone: 0.4,
    sfxVolume: 0.5,
    sfx: true, // false يطفي كل المؤثرات
  },

  grade: {
    // الكريد السينمائي الأساسي محروق بالفيديو من luts/nabd-cinematic.cube (يفتح بدافنشي).
    // هاي طبقات فوقه بس — 0 يطفيها
    warmHighlights: 0,
    tealShadows: 0,
    shadowTint: '20,33,58',
    vignette: 0.1,
    grain: 0.035,
    lightLeak: 0,
  },
};

export const totalSeconds = content.outro.start + content.outro.duration;
