if(typeof(toolkit.rh.relatorio) == 'undefined') {
    Ext.ns('toolkit.rh.relatorio');

    toolkit.rh.relatorio.CarteiraFuncional = Ext.extend(
        Ext.Panel,
        {

            _not_implemented: function(){
                console.debug("not implemented");
            },

            constructor: function(type) {
                var cf = {
                    title: 'Formulários',
                    closable: true,
                    type: type,
                    width: 940
                };

                toolkit.rh.relatorio.CarteiraFuncional.superclass.constructor.call(this, cf);

                var active = toolkit.Application.tabspace.getActiveTab();
                toolkit.Application.tabspace.remove(active);
                toolkit.Application.tabspace.add(this);

                this.setPanel(this.getPanelCarteiraFuncional());

                var obj = this;
                setTimeout(function() {obj.doLayout();}, 50);
            },

            setPanel: function(panel){
//                if(this.activePanel){
//                    this.remove(this.activePanel);
//                }
                this.removeAll();
                this.activePanel = panel;
                this.add(panel);
                this.doLayout();
//                var obj = this;
//                setTimeout(function() {obj.doLayout();}, 50);
            },

            /*****
             *
             *    PANEL APRESENTAÇÃO
             *
             **/
            getPanelCarteiraFuncional: function(){
                try{
                    if(!this.panelCarteiraFuncional){
                        this.panelCarteiraFuncional = new Ext.Panel({
                            layout: "form",
                            title: "Formulários",
                            border: false,
                            buttonAlign: "center",
                            items:[
                                {
                                    width: 600,
                                    name: "servidores",
                                    id:"MSServidores",
                                    fieldLabel: "Servidores",
                                    xtype: "multiselectbox",
                                    toSearch: [],
                                    allowBlank: true,
                                    validateOnBlur: true,
                                    model: {
                                        name: "Servidor",
                                        pkg: "rh.models"
                                    },
                                    controller: "RHServidor"
                                 },
                                         {
                                name: "foto",
                                id: "fotoId",
                                fieldLabel: "Foto",
                                xtype: "combobox",
                                allowBlank: false,
                                validateOnBlur: true,
                                blankText: "É necessário preencher este campo.",
                                store: new Ext.data.SimpleStore({
                                    fields: ['id', 'description'],
                                    data: [["s", "SOMENTE COM FOTO"], ["t", "INDEPENDENTE DE FOTO"]]
                                    }),
                                displayField: 'description',
                                typeAhead: true,
                                mode: "local",
                                triggerAction: 'all',
                                emptyText:'Selecione um item...',
                                selectOnFocus:true,
                                editable: true}
                            ],
                            buttons: [
                                {
                                    text: "Gerar Relatório",
                                    iconCls: true,
                                    icon: "/" + global.Context + "/static/images/application-pdf.png",
                                    handler: function() {
                                        var s = this.findById("MSServidores").grid.store.data.items;
                                        var selecteds = [];
                                        for(var i = 0, len = s.length; i < len; i++){
                                            selecteds[i] = s[i].data["pk"];
                                        }
                                        new toolkit.widget.ExtReportBuild(
                                            'RHPrintCarteiraFuncional',
                                            '/to/mpe/rh/carteira_funcional/carteira_4_1'
                                        ).runReport(
                                            '',
                                            {
                                                servidores: selecteds
                                            }
                                        )
                                    },
                                    scope: this
                                }
                            ]
                        });
                    }
                    return this.panelCarteiraFuncional;
                }catch(e){alert(e);return null;}
            },

            getFormularioColumnModel: function() {
                return new Ext.grid.ColumnModel([
                    {
                        key: 'id',
                        header: 'Chave',
                        width: 50
                    },
                    {
                        key: 'description',
                        header: 'Nome',
                        width: 550
                    }
                ]);
            },

            getFormularioGridPaginator: function() {
                if(!this.gridPaginator) {
                    this.gridPaginator = new Ext.PagingToolbar({
                        store: [],
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    })
                }

                return this.gridPaginator;
            },

            getFormularioGridStore: function() {
//                if(!this.gridStore) {
                    this.gridStore = new Ext.data.JsonStore({
                        fields: ['id','description'],
                        root: 'result',
                        totalProperty: 'totalRows',
                        url: toolkit.util.Normalize.controller_action(
                            'EDOCFormulario',
                            'get_formulario'
                        )
                    });

                    this.gridStore.load({
                        params: {
                            sort: 'id',
                            dir: 'DESC'
                        }
                    });
//                }
                return this.gridStore;
            }
    });
}