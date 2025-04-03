import type { Meta, StoryObj } from '@storybook/angular';
import { MpmtVerMaisComponent } from './mpmt-ver-mais.component';
import { moduleMetadata } from '@storybook/angular';
import { LayoutPadraoModalComponent } from 'layout/mpmt-modal/layout-padrao-modal.component';

const meta: Meta<MpmtVerMaisComponent> = {
  title: 'Components/MpmtVerMais',
  component: MpmtVerMaisComponent,
  decorators: [
    moduleMetadata({
      declarations: [LayoutPadraoModalComponent],
    }),
  ],
  args: {
    data: {
      titulo: 'Exemplo de Modal',
      conteudo: '<p><strong>Este é um texto em negrito!</strong> <br> E este é um <em>texto em itálico</em>.</p>'
    },
  },
};

export default meta;
type Story = StoryObj<MpmtVerMaisComponent>;

export const Default: Story = {
  render: (args) => ({
    props: args,
    template: `
      <layout-padrao-modal [title]="data.titulo" (close)="fechar()">
        <div [innerHTML]="data.conteudo"></div>
      </layout-padrao-modal>
    `,
  }),
};
