/**
 *
 **/
Ext._define('edocs.processo.consulta.processoComumGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.processo.consulta.processoComumWindow',

    keywordFieldMessage: '',

    hideItemsToolbar: ['add','edit', 'remove', 'download'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Protocolo', dataIndex: 'codigo', width: 130, hidden: true, sortable: true},
                    {header: 'Processo', dataIndex: 'codigo_processo', width: 160, sortable: true},
                    {header: "P. Externo", dataIndex: 'protocolo_externo', width: 130, hidden: true, sortable: true},
                    {header: "Movimentado", dataIndex: "movimentado", sortable: true},
                    {header: "Assunto", dataIndex: "assunto_display", width: 180, sortable: true},
                    {header: "Custo", dataIndex: "custo", sortable: true, width: 70},
                    {header: "Remetente", dataIndex: "remetente", width: 200},
                    {header: "Localização atual", dataIndex: "posicao", id: 'autoExpandColumn'},
                    {header: "Situação", dataIndex: "situacao_display", width: 180, sortable: true},
                    {header: 'Página', dataIndex: 'paginas', width: 60, sortable: true},
                    {header: 'Volume', dataIndex: 'volume', width: 60, sortable: true},
                ]
            );

        return this._columnModel;
    },

    getConfigItemsToolbar: function() {
        var menu = [];
        menu.push({
            text: "Abrir",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/document-open.png",
            handler: function() {
                if(this.getSelectionModel().getSelected()) {
                    this.openItem();
                }
                else
                    Ext.Msg.show({
                        title: 'Visualizar',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Primeiro selecione um item.'
                    });
            },
            scope: this
        });
        menu.push("-");
        menu.push({
            text: "Imprimir",
            iconCls: true,
            icon: "/" + global.Context + "/static/images/application-pdf.png",
            menu: [{
                text: "Todo andamento",
                iconCls: true,
                handler: function() { this._imprimir_protocolo(); },
                scope: this
            }]
        });
        menu.push("-");
        menu.push("Busca Rápida : ");
        menu.push(" ");
        menu.push(this.getKeywordField());
        menu.push("-");
        return menu;
    },

    _imprimir_protocolo: function() {
        var codigo;
        var selected = this.getSelectionModel().getSelected();
            if(selected) {
                codigo = selected.get("codigo");
                 engine.mq.Report.request({
                    report: '/to/mpe/protocolo/athenas/documento_movimentacoes',
                    waitMessage: 'Gerando relatório...',
                    params: Ext.apply(
                        {
                            outfile: 'ferias_usufruir',
                            report_name: 'Férias a Usufruir no Mês',
                            protocolo: codigo,
                        }
                    ),
                });
            }
            else
                Ext.Msg.show({
                    title: 'Imprimir Protocolo',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Selecione um processo'
                });
    },

    openItem: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            Ext._create('edocs.processo.openWindow', {
                action: 'update',
                oId: selected.get('id'),
                values: selected.data,
                params: this.getParams(),
            }).show();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg,{
           autoExpandMin: 210,
        });

        Ext.apply(cfg,{
            doubleClickHandler: this.openItem,
            allowCreate: false,
            allowUpdate: false,
            allowRemove: false,
            columnAction: false,
        });

        edocs.processo.consulta.processoComumGrid.superclass.constructor.call(this, cfg);
    }

});
