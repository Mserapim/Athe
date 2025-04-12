/**
 *
 **/

Ext._define('rh.ferias.reports.Collaborator', {
    extend: 'toolkit.widget.TabPanel',

    _buildReport: function(type){
        if(this.getYearField().getValue() && this.getWorkplace().getValue()){
            engine.mq.Report.request({
                report: '/to/mpe/rh/ferias/Employee_Holidays',
                waitMessage: 'Gerando relatório...',
                params: {
                    ano: this.getYearField().getValue(),
                    local: this.getWorkplace().getValue(),
                }
            }, type);
        }else Ext.Msg.show({
            msg: 'Selecione Lotação e Ano',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

    getYearField: function() {
        if (!this._year)
            this._year = Ext._create('Ext.form.TextField', {
                name: 'year',
                fieldLabel: "Ano",
                hidden: false,
                width: 350,
            });
        return this._year;
    },

    getWorkplace: function(cfg){
        if(!this._workplace){
            this._workplace = Ext._create('core.fields.AutocompleteField', {
                name: 'workplace',
                rest: 'rh.workplace.Restful',
                fieldLabel: 'Lotação',
                width: 350
            });
            var workplace = [];
            for (var i = cfg.workplace_responsible.length - 1; i >= 0; i--)
                workplace.push(cfg.workplace_responsible[i]);
            this._workplace.setPreFilter([{
                property: 'pk__in',
                value: workplace,
                stage: 0,
            }]);
        }
        return this._workplace;
    },

    getMain: function(cfg){
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
                items: [
                {
                    xtype: 'fieldset',
                    title: 'Relatório Férias de Colaboradores',
                    name: 'fieldServidor',
                    width: 500,
                    style: 'margin: 5px',
                    align: 'center',
                    items:[

                        this.getWorkplace(cfg),
                        this.getYearField(),
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Relatório',
                        width: 100,
                        height: 25,
                        scope: this,
                        // handler: this._buildReport,
                        menu: {
                            scope: this,
                            items: [
                                {
                                    text: 'Arquivo PDF ',
                                    type: 'PDF',
                                    iconCls: 'icon-ged icon-ged-application-pdf',
                                    scope: this,
                                    handler: function (item) {
                                        this._buildReport(item.type);
                                    }
                                },
                                {
                                    text: 'Arquivo ODT',
                                    type: 'ODT',
                                    iconCls: 'icon-ged icon-ged-application-msword',
                                    scope: this,
                                    handler: function (item) {
                                        this._buildReport(item.type);
                                    }
                                },
                                {
                                    text: 'Arquivo XLS',
                                    type: 'XLS',
                                    iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                    scope: this,
                                    handler: function (item) {
                                        this._buildReport(item.type);
                                    }
                                },
                            ]
                        },
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
        Ext.applyIf(cfg,{title: 'Relatório -> Férias Colaboradores'});
        Ext.apply(
            cfg,
            {
                layout: 'border',
                items:[ 
                    this.getMain(cfg),
                ]
            }
        );
        rh.ferias.reports.Collaborator.superclass.constructor.call(this, cfg);
    }
});