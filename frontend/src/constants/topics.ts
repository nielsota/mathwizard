export interface TopicMeta {
  slug: string
  label: string
  subtitle: string
  icon: string
}

export const TOPICS: TopicMeta[] = [
  {
    slug: 'unitcircle',
    label: 'Eenheidscirkel',
    subtitle: 'Sinus, cosinus en tangens op de eenheidscirkel',
    icon: '⊙',
  },
  {
    slug: 'derivatives',
    label: 'Afgeleiden',
    subtitle: 'Differentiëren en afgeleide functies',
    icon: "f'",
  },
  {
    slug: 'rootfinding',
    label: 'Wortels vinden',
    subtitle: 'Snijpunten, nulpunten en vergelijkingen oplossen',
    icon: '√',
  },
  {
    slug: 'parametric',
    label: 'Parametrische vergelijkingen',
    subtitle: 'Parametrische krommen en vergelijkingen',
    icon: 't→',
  },
  {
    slug: 'goniometrie',
    label: 'Goniometrie',
    subtitle: 'Goniometrische functies, identiteiten en vergelijkingen',
    icon: 'θ',
  },
]

export const TOPIC_MAP: Record<string, TopicMeta> = Object.fromEntries(
  TOPICS.map(topic => [topic.slug, topic]),
)
