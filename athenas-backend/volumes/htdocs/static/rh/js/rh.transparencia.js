Ext.ns('toolkit.rh.transparencia');


Ext.apply(
    toolkit.rh.transparencia,
    {
        //----------------------------------------------------------------------------
        Reports: Ext.extend(
            Ext.Panel,
            {
                constructor: function(params, callback){
                    var cf = {
                        title: 'Relatórios - Portal Tranparência',
                        border: false,
                        closable: true,
                        items: [
                            this.getFormPanel()
                        ],
                        autoScroll: false,
                        relatorio: null
                    };

                    toolkit.rh.transparencia.Reports.superclass.constructor.call(this, cf);

                    var ts = toolkit.Application.tabspace;

                    ts.remove(ts.getActiveTab());
                    ts.add(this);
                    ts.setActiveTab(this);
                },
                _buildDocumento: function(){
                    if(this.relatorio){
                        var report_src = '/to/mpe/portaltransparencia/rh/' + this.relatorio;
                        console.debug(report_src);
                        new toolkit.widget.ExtReportBuild(
                            'PTReports',
                            report_src
                        ).runReport( '', {report: this.relatorio});
                    }else{
                        alert("Selecione o relatório que deseja gerar.");
                    }
                },
                getFormPanel: function(){
                    this.panel = new Ext.Panel({
                        closable: true,
                        border: false,
                        defaults: {
                            style: 'margin: 5px 20px',
                            xtype:'fieldset',
                            collapsible: true,
                            buttons: [{
                                text: "Gerar",
                                handler: this._buildDocumento,
                                scope: this
                            }]
                        },
                        buttonAlign: 'center',
                        labelWidth: 120,
                        labelAlign: 'right',

                        items: [
                            {
                                title: "Relatórios Gerais",
                                items: [
                                    {
                                        fieldLabel: 'Relatório',
                                        xtype: 'combo',
                                        hiddenName: 'relatorio',
                                        store: [
                                                ['afastados', 'Afastados'],
                                                ['aposentados', 'Aposentados'],
                                                ['cedidos', 'Cedidos'],
                                                ['estagiarios', 'Estagiarios'],
                                                ['membros', 'Membros'],
                                                ['pensionistas', 'Pensionistas'],
                                                ['requisitados', 'Requisitados'],
                                                ['servidores_comissionados', 'Servidores Comissionados'],
                                                ['servidores_efetivos', 'Servidores Efetivos']
                                            ],
                                        triggerAction: 'all',
                                        editable: false,
                                        listeners:{
                                            select: function(cmb, rec, idx)
                                            {
                                               console.debug(cmb.getValue());
                                               this.relatorio = cmb.getValue();
                                            },
                                            scope: this
                                        }
                                    }
                                ],
                                scope: this
                            },{
                                title: "Outros Requerimentos",
                                items: [

                                ],
                                scope: this
                            }
                        ],
                        scope: this
                    });
                    return this.panel;
                }
            }
        )
        //----------------------------------------------------------------------------
    }

);

