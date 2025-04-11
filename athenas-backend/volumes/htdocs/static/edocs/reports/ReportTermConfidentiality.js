Ext._define('edocs.reports.ReportTermConfidentiality', {
    extend: 'toolkit.widget.TabPanel',

    _buildReport: function(){

        var orgao_id = this.getOrgao().getValue();

        engine.mq.Report.request({
            report: '/to/mpe/protocolo/term_commitment_maintain_confidentiality',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'relatorio_termo_confidencialidade',
                report_name: 'Relatório Extrato de Termo de Confidencialidade',
                orgao_id: orgao_id != "" ? orgao_id : null
            }

        });
    },

    getOrgao: function(){
        if(!this._orgao)
            this._orgao = Ext._create('core.fields.AutocompleteField', {
                name: 'orgao_id',
                rest: 'rh.generalorgan.Restful',
                fieldLabel: 'Orgão ',
                width: 350
            });

        return this._orgao;
    },

    getMain: function(){
        if(!this._panel)
        this._panel = new Ext.Panel({
            layout: 'border',
            region: 'center',
            height: 650,
            split: true,
            autoEl: {tag: 'center'},
            items: [
            {
                region: 'center',
                border: false,
                autoScroll: true,
                items: [
                {
                    xtype: 'fieldset',
                    title: 'EDOCS -> Termo de Confidencialidade',
                    name: 'fieldServidor',
                    width: 650,
                    style: 'margin: 5px',
                    align: 'center',
                    items:[
                        this.getOrgao(),
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Relatório',
                        width: 100,
                        height: 25,
                        scope: this,
                        handler: this._buildReport,
                    },
                    ]
                },
                ]
            }
            ]
        });

        return this._panel;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Termo de Confidencialidade'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items:[ 
                    this.getMain(),
                ]
            }
        );
        edocs.reports.ReportTermConfidentiality.superclass.constructor.call(this, cfg);
    }
});