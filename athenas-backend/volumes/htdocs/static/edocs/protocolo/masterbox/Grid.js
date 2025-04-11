Ext._define('edocs.protocolo.masterbox.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.protocolo.masterbox.Window',

    keywordFieldMessage: 'protocolo, assunto, protocolo externo, chancela',

    getMenuAction: function(cfg) {
        if (!this._menuAction) {
            this._menuAction = Ext._create('Ext.Button', {
                text: 'Ações',
                scope: this,
                iconCls: 'icon-edocs icon-protocolo-actions',
                menu: this.getMenuItems(cfg),
            });
        }
        return this._menuAction;
    },

    getMenuItems: function(cfg) {
        return [
            {
                text: 'Visualizar fluxograma do protocolo',
                iconCls: 'icon-edocs icon-protocolo-flowchart',
                scope: this,
                handler: this.generateFlowchart
            },
        ];
    },

    generateFlowchart: function () {
        var selected = this.getSelectionModel().getSelected();

        if (selected) {
            edocs.reports.Flowchart.generate({
                el: this.getEl(),
                waitMessage: 'Gerando fluxograma...',
                params: {
                    protocol: selected.get('pk'),
                    output_format: 'pdf'
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Fluxograma',
                msg: 'Selecione o protocolo para o qual deseja gerar o fluxograma.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    __rendererItem: function(value, cell, data) {
        var tpl = new Ext.XTemplate(
            '<div class="edoc-row">',
                '<div class="edoc-item">',
                    '<div>',
                        '<div class="subject inline-with-crop" ext:qtip="Assunto">{assunto}</div>',
                    '</div>',
                    '<div>',
                        '<div class="subject inline-with-crop" ext:qtip="Interessado">{interessado_unicode}</div>',
                    '</div>',
                    '<div class="two-column">',
                        '<div class="one" ext:qtip="Protocolo">{codigo}</div>',
                        '<div class="two" ext:qtip="Data de criação">{data_criacao}</div>',
                    '</div>',
                '</div>',
            '</div>'
        );
        var row = {};
        Ext.apply(row, data.data);
        row.data_criacao = Ext.util.Format.date(row.data_criacao, 'd/m/Y H:i');

        return tpl.apply(row);
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {
                        menuDisabled: true,
                        id: 'autoExpandColumn',
                        dataIndex: '__ghost__',
                        header: 'Descrição',
                        renderer: this.__rendererItem
                    }
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'edocs.protocolo.masterbox.Restful',
    'edocs.protocolo.masterbox.Grid'
);
