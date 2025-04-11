/**
 *
 **/
Ext._define('rh.pesquisa.PrevidenciarioRestfulGrid', {
    'extend': 'core.RestfulGrid',

    'restWindow': 'rh.pesquisa.PrevidenciarioRestfulWindow',

    'keywordFieldMessage': 'Servidor, Empresa/Orgão',

    'getColumnModel': function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        dataIndex: 'servidor_unicode',
                        header: 'Servidor',
                        width: 200,
                        id: 'autoExpandColumn',
                        hidden: true
                    },
                    {
                        dataIndex:'data_nascimento', 
                        header:'Data de Nascimento', 
                        width:110,
                    },
                    {
                        dataIndex:'idade', 
                        header:'Idade', 
                        width:50,
                    },
                    {
                        dataIndex:'tipo_regime_display', 
                        header:'Tipo de Regime', 
                        width:210,
                        // id: 'autoExpandColumn'
                    },
                    {
                        dataIndex:'empresa_orgao', 
                        header:'Empresa/Orgão', 
                        width:285
                    },
                    {
                        dataIndex:'data_inicio', 
                        header:'Data Início', 
                        width:80,
                    },
                    {
                        dataIndex:'data_fim', 
                        header:'Data Fim', 
                        width:80,
                    },
                    {
                        dataIndex:'dias', 
                        header:'Dias', 
                        width:80
                    }
                ]
            );

        return this._columnModel;
    },

    'changeFitlerTipo': function(tipo) {
        if(tipo) {
            this.setFilterProperty('tipo', tipo, 0);
        }
        else
            this.removeFilterProperty('tipo');
    },

    'changeFilterPrincipal': function(enable) {
        if(enable)
            this.setFilterProperty('principal', true, 1);
        else
            this.removeFilterProperty('principal');
    },

    'filterServidor': function(){
         var wnd = Ext._create('Ext.Window', {
            'title': 'Selecionar Servidor',
            'modal': true,
            'resizable': false,
            'width': 450,
            'border': false,
            'buttons': [
                {
                    'text': 'Selecionar',
                    'scope': this,
                    'handler': function() {
                        var form = wnd.getComponent(0).getForm();

                        if(form.getValues().selecionado)
                            this.setFilterProperty('servidor', form.getValues().selecionado, 1002);
                        else
                            this.removeFilterProperty('servidor', 1002);

                        wnd.destroy();
                    }
                },
                {
                    'text': 'Fechar',
                    'scope': this,
                    'handler': function() {
                        wnd.destroy();
                    }
                }
            ],
            'items': Ext._create('Ext.form.FormPanel', {
                'frame': true,
                'items': [
                    {
                        'xtype': 'autocompletefield',
                        'fieldLabel': 'Servidor',
                        'hiddenName': 'selecionado',
                        'crudController': 'RHServidor',
                        'queryAction': 'query',
                        'queryParam': 'keyword',
                        'displayField': 'description',
                        'valueField': 'pk',
                        'width': 300,
                        'hideTrigger': true,
                        'emptyText': 'Insira a matrícula ou o nome do servidor'
                    }
                ]
            })
        }).show();

    },

    'togglePrevidenciario': function(tipo) {
        if(this._filterEscolaridade.indexOf(tipo) >= 0)
            this._filterEscolaridade.remove(tipo);
        else
            this._filterEscolaridade.push(tipo);

        this.setFilterProperty('tipo_regime__in', this._filterEscolaridade, 1000);
    },

    'cleanFilter': function() {
        this._filterEscolaridade = [1, 2];
        this.setFilter([
            {'property': 'tipo_regime__in', 'value': this._filterEscolaridade, 'stage': 1000},
        ]);
    },

    'getFilterMenu': function() {
        if(!this._filterMenu)
            this._filterMenu = [
                {
                    'text': 'Por Servidor',
                    'scope':this,
                    'handler':this.filterServidor
                },
                '-',
                {
                    'text': 'Por Regime',
                    'menu': [
                        {
                            'text': 'Regime Geral',
                            'checked': true,
                            'scope': this,
                            'handler': function() { this.togglePrevidenciario(1) }
                        },
                        {
                            'text': 'Regime Próprio',
                            'checked': true,
                            'scope': this,
                            'handler': function() { this.togglePrevidenciario(2) }
                        }
                    ]
                },
            ];

        return this._filterMenu;
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        rh.pesquisa.PrevidenciarioRestfulGrid.superclass.constructor.call(this, cfg);

        this.cleanFilter()
    }

})