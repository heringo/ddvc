<script lang="ts" setup>
import {
  VisXYContainer,
  VisStackedBar,
  VisAxis,
  VisBulletLegend,
  VisTooltip
} from '@unovis/vue';

import {
  FitMode,
  Sankey,
  Sizing,
  Position,
  SankeySubLabelPlacement,
  VerticalAlign
} from '@unovis/ts';

import { VisSingleContainer, VisSankey } from '@unovis/vue';
import { ref } from 'vue';

export type Node = {
  id: string;
  label: string;
  value: number;
  subgroups: Node[];
  color?: string;
  expandable?: boolean;
  expanded?: boolean;
};

export type Link = { source: string; target: string; value: number };

export type Sankey<N, L extends Link> = {
  nodes: N[];
  links: L[];
  expand: (n: any) => void;
  collapse: (n: any) => void;
};

const data = {
  sankey: [
    {
      label: 'Employees',
      color: '#f3e4b2',
      value: 0.1
    },
    {
      label: 'Website traffic',
      value: 0.38,
      color: '#54df56'
    },
    {
      label: 'Socials',
      value: 0.11,
      color: '#67d469',
      subgroups: [
        {
          label: 'Twitter',
          value: 0.09,
          color: '#67d469'
        },
        {
          color: '#67d469',
          label: 'LinkedIn',
          value: 0.02
        }
      ]
    },
    {
      label: 'Mobile',
      value: 0.2,
      color: '#f7d1b5',
      subgroups: [
        {
          color: '#67d469',
          label: 'DAU',
          value: 0.1
        },
        {
          color: '#f7b5b5',
          label: 'Downloads',
          value: 0.1
        }
      ]
    },
    {
      label: 'Reviews',
      color: '#f3e4b2',
      value: 0.205,
      subgroups: [
        {
          label: 'ProductHunt',
          value: 0.06
        },
        {
          label: 'G2',
          value: 0.01
        },
        {
          label: 'TrustPilot',
          value: 0.14
        }
      ]
    },
    {
      label: 'GitHub',
      value: 0.0,
      color: 'gray'
    }
  ],
  statusCode: 200
};

const getNodes = (n: Node): Node[] =>
  n.subgroups?.map((child, i) => ({
    ...child,
    id: [n.id, i].join(''),
    color: child.color ?? n.color,
    expanded: false,
    expandable: child.subgroups?.length > 0
  }));

const getLinks = (n: Node): Link[] =>
  n.subgroups.map((target) => ({
    source: n.id,
    target: target.id,
    value: target.value
  }));

const generate = (n: Node): Node => ({ ...n, subgroups: getNodes(n) });

const total = data.sankey.reduce((acc, curr) => acc + curr.value, 0);

const root: Node = generate({
  id: 'root',
  label: 'Weights',
  value: total,
  color: 'lightgray',
  expanded: true,
  expandable: false,
  subgroups: data.sankey as Node[]
});

const sankeyData: Sankey<Node, Link> = {
  nodes: [root, ...root.subgroups],
  links: getLinks(root),
  expand: function (n: any): void {
    console.log('EXPANDING');
    n.subgroups = getNodes(n);
    this.nodes[n.index].expanded = true;
    this.nodes = this.nodes.concat(n.subgroups);
    this.links = this.links.concat(getLinks(n));
  },
  collapse: function (n: any): void {
    this.nodes[n.index].expanded = false;
    this.nodes = this.nodes.filter(
      (d) => d.id === n.id || !d.id.startsWith(n.id)
    );
    this.links = this.links.filter((d) => !d.source.startsWith(n.id));
  }
};

const transformedData = ref({
  nodes: sankeyData.nodes,
  links: sankeyData.links
});

function toggleGroup(n: any): void {
  if (n.expandable) {
    if (n.expanded) {
      sankeyData.collapse(n);
    } else {
      sankeyData.expand(n);
    }
    transformedData.value = {
      nodes: sankeyData.nodes,
      links: sankeyData.links
    };
  }
}

const callbacks = {
  linkColor: (d: any): string => d.target.color ?? null,
  nodeCursor: (d: Node) => (d.expandable ? 'pointer' : null),
  nodeIcon: (d: Node): string => (d.expandable ? (d.expanded ? '-' : '+') : ''),
  subLabel: (d: any): string =>
    d.depth === 0 || d.expanded
      ? ''
      : `${((d.value / root.value) * 100).toFixed(1)}%`,
  events: {
    [Sankey.selectors.node]: {
      click: toggleGroup
    }
  }
};

const subLabel = (d: any) => {
  // if (d.links.every((link: any) => link.source.id == "root")) return "";
  if (d.sourceLinks.length > 0) return '';

  const value = d.value;
  const percentage = d.links[0].source
    ? `${((value / total) * 100).toFixed(2)}%`
    : '';

  return percentage;
};

const props = defineProps<{
  height: number;
}>();

const { height } = toRefs(props);
const internalHeight = ref(0);

watch(height, async () => {
  await nextTick();
  internalHeight.value = height.value;
});

onMounted(async () => {
  await nextTick();
  internalHeight.value = height.value;
});

const margin = { left: -120, right: 0 };
</script>

<template>
  <!--:margin="{ left: -30, right: -30 }"
-->
  <VisSingleContainer
    :data="transformedData"
    :height="internalHeight"
    :margin="margin"
  >
    <VisSankey
      v-bind="callbacks"
      :labelFit="FitMode.Wrap"
      :labelVerticalAlign="VerticalAlign.Middle"
      :labelForceWordBreak="false"
      :nodePadding="10"
      :labelPosition="Position.Left"
      :subLabel="subLabel"
    />
  </VisSingleContainer>
</template>
