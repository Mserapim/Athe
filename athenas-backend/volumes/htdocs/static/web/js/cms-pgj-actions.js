if(!toolkit.web.cms.pgjActions)
{
    toolkit.web.cms.pgjActions = Ext.extend(toolkit.widget.TabPanel, {
        constructor: function(site, kind, area, area_title, permissions, title)
        {
            this.site = site;
            this.kind = kind;
            this.area = area;
            this.area_title = area_title;
            this.perms = permissions;
            var options = {
                title: title,
                layout: 'fit',
                closable: true,
                defaults: {margins: '2 2 2 2'}
            };

            toolkit.web.cms.pgjActions.superclass.constructor.call(this, options);
            //toolkit.Application.tabspace.add(this);

            this.store = new Ext.data.JsonStore({
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                remoteSort: true,
                fields: ['id', 'title', 'filing', 'text', 'marked_as_published', 'content',
                'published', 'published_date', 'publication_start', 'publication_end',
                'start_date', 'decision_date', 'status', 'status_id', 'county', 'county_id'],
                url: action('CMS/get_prosecutor_actions/json'),
                baseParams: { start: 0, limit: 20, area: this.area },
                scope: this,
                listeners: {
                    load: function()
                    {
                        Ext.select('.athenas-delete').set({src: icons+'delete.png'});
                        Ext.select('.athenas-published').set({src: icons+'published.png'});
                        Ext.select('.athenas-non-published').set({src: icons+'no-published.png'});
                    },
                    scope: this
                }
            });
            new Ext.LoadMask(Ext.getBody(), {msg: 'Por favor aguarde...', store: this.store});
            this.add(this.getProsecutorActions());
            this.doLayout();
        },

        getProsecutorActions: function()
        {
            if(!this.actions)
            {
                this.actions = new Ext.grid.GridPanel({
                    scope: this,
                    store: this.store,
                    tbar:
                    [
                        {
                            tooltip:'Nova atuação',
                            icon: icons+'add.png',
                            text: 'Nova',
                            handler: function()
                            {
                                this.makeForm({
                                    title: 'Adicionar atuação',
                                    vals: {
                                        area: this.area
                                    }
                                }).show();
                            },
                            scope: this
                        },
                        '-',
                        {
                            tooltip: 'Áreas',
                            icon: icons+'show-areas.png',
                            text: 'Áreas',
                            handler: function()
                            { getAreaManager(this.site, this.kind, this.perms, this.area_title, true); },
                            scope: this
                        },
                        {
                            tooltip: 'Visualizar fases de atuação',
                            icon: icons+'status.png',
                            text: 'Fases de atuação',
                            handler: function()
                            { getPGJActionStatusesManager(true); }
                        }
                    ],
                    columns:
                    [
                        {
                            dataIndex: 'title', header: 'Auto', width:450,
                            renderer: function(val){ return toolkit.util.replaceAll(val, '\\', ''); }
                        },
                        {dataIndex: 'status', header: 'Andamento', width: 150},
                        {
                            xtype: 'actioncolumn',
                            width: 115,
                            scope: this,
                            items: [
                                {
                                    tooltip: 'Publicação',
                                    getClass: function(v, meta, rec, a, b)
                                    { return rec.get('marked_as_published') ? 'athenas-published' : 'athenas-non-published'; },
                                    handler: function(grid, row, col)
                                    {
                                        var pubForm = makePublicationForm({
                                            title: 'Publicação da atuação',
                                            store: this.store,
                                            record: this.store.getAt(row)
                                        });
                                    },
                                    scope: this
                                },
                                // {
                                //     tooltip: 'Anexos',
                                //     icon: icons+'attach.png',
                                //     handler: function(grid, row, col)
                                //     {
                                //         var record = grid.getStore().getAt(row);
                                //         getAttachmentsManager(record.get('id'), record.get('title'), true);
                                //     },
                                //     scope: this
                                // },
                                // {
                                //     tooltip: 'Obter endereço do post',
                                //     icon: icons + 'get_link.png',
                                //     scope:this,
                                //     handler: function(grid, row, col)
                                //     {
                                //         var keyMap = null;
                                //         var record = grid.getStore().getAt(row);
                                //         new xWindow({
                                //             id:'URL-window',
                                //             title: 'Endereço de Post',
                                //             modal:true,
                                //             items:
                                //             [
                                //                 {
                                //                     id:'url-to-copy',
                                //                     xtype:'textfield',
                                //                     fieldLabel: 'URL',
                                //                     selectOnFocus:true,
                                //                     value: record.get('link'),
                                //                     readOnly: true,
                                //                     width:400
                                //                 },
                                //                 {
                                //                     id:'url-hint',
                                //                     xtype:'displayfield',
                                //                     html:'<span>Tecle CTRL+C para copiar</span>'
                                //                 },
                                //                 {
                                //                     id:'select-url',
                                //                     xtype:'button',
                                //                     text:'Selecionar',
                                //                     handler: function(btn)
                                //                     {
                                //                         btn.ownerCt.findById('url-to-copy').focus();
                                //                         btn.setValue('Selecionar');
                                //                     }
                                //                 }
                                //             ],
                                //             listeners:{
                                //                 show:function(component)
                                //                 {
                                //                     keyMap = new Ext.KeyMap( component.el,
                                //                         {
                                //                             key: 'c',
                                //                             ctrl:true,
                                //                             fn: function()
                                //                             {
                                //                                 var btnSelect = component.findById('select-url');
                                //                                 btnSelect.setText('Copiado!');
                                //                                 setTimeout(function(){ btnSelect.setText('Selecionar'); }, 1000);
                                //                             }
                                //                         }
                                //                     );
                                //                     component.findById('url-to-copy').focus(true, 100);
                                //                 },
                                //                 destroy: function()
                                //                 { keyMap.disable(); }
                                //             }
                                //         }).show();
                                //     }

                                // },
                                {
                                    tooltip: 'Editar',
                                    icon: icons+'edit.png',
                                    handler: function(grid, row, col)
                                    {
                                        var record = grid.getStore().getAt(row);
                                        this.makeForm({
                                            title: 'Editar atuação',
                                            vals: {
                                                area: this.area,
                                                id: record.get('id'),
                                                title: record.get('title'),
                                                filing: record.get('filing'),
                                                text: record.get('text'),
                                                start_date: record.get('start_date'),
                                                decision_date: record.get('decision_date'),
                                                status: record.get('status'),
                                                status_id: record.get('status_id'),
                                                county: record.get('county'),
                                                county_id: record.get('county_id')
                                            }
                                        }).show();
                                    },
                                    scope:this
                                },
                                {
                                    tooltip: 'Excluir',
                                    getClass: function(v, meta, rec, a, b)
                                    { return 'athenas-delete'; },
                                    handler: function(grid, row, col)
                                    {
                                        var rec = grid.getStore().getAt(row);

                                        xConfirm({
                                            title: 'Confirmação',
                                            msg: 'Confirma a exclusão da atuação: '+ rec.get('title') +' ?',
                                            fn: function(btn)
                                            {
                                                deleteItem({
                                                    signal: btn,
                                                    model: 'ProsecutorAction',
                                                    pars: rec.get('id'),
                                                    store: grid.getStore()
                                                });
                                            }
                                        });

                                    },
                                    scope:this
                                }
                            ]
                        }
                    ],
                    bbar: new Ext.PagingToolbar({
                        store: this.store,
                        displayInfo: true,
                        pageSize: 20,
                        prependButtons: true
                    })
                });
            }
            return this.actions;
        },

        makeForm: function(opts)
        {
            var combo = new Ext.form.ComboBox({
                hiddenName: 'status',
                fieldLabel: 'Fase atual',
                hiddenValue: opts.vals.status_id || '',
                value: opts.vals.status || '',
                mode: 'local',
                triggerAction: 'all',
                width: 320,
                valueField: 'id',
                displayField: 'name',
                store: new Ext.data.JsonStore({
                    autoLoad: true,
                    root: 'result',
                    totalProperty: 'total',
                    fields: ['id', 'name'],
                    proxy: new Ext.data.HttpProxy({
                        method: 'GET',
                        url: action('CMS/get_prosecutor_action_statuses/json')
                    })
                })
            });

            var addButton = {
                xtype: 'button',
                icon: icons+'add.png',
                tooltip: 'Adicionar nova fase',
                handler: function()
                {
                    new toolkit.web.cms.pgjActionsStatus().makeForm({
                        vals: {},
                        store: combo.getStore(),
                        success: function(form, action)
                        {
                            combo.getStore().on('load', function(){
                                combo.setValue(action.result.data);
                            });
                        }
                    }).show();
                }
            };

            return new ExtFormHelper({
                url: action('CMS/add_or_edit_prosecutor_action/json'),
                store: this.store,
                windowConfig: {
                    title: opts.title,
                },
                formConfig: {
                    autoWidth: true,
                    autoScroll: true,
                    height: 500,
                    defaults: {
                        style: {
                            marginBottom: '7px'
                        }
                    },
                    items: [
                        {
                            name: 'area',
                            value: opts.vals.area || '',
                            xtype: 'hidden'
                        },
                        {
                            name: 'id',
                            value: opts.vals.id || '',
                            xtype: 'hidden'
                        },
                        {
                            name: 'title',
                            fieldLabel :'Auto nº',
                            value: toolkit.util.replaceAll(opts.vals.title, '\\', '') || '',
                            xtype: 'textfield',
                            width: 320
                        },
                        {
                            xtype: 'combo',
                            hiddenName: 'county',
                            fieldLabel: 'Comarca',
                            hiddenValue: opts.vals.county_id || '',
                            value: opts.vals.county || '',
                            mode: 'local',
                            triggerAction: 'all',
                            width: 320,
                            valueField: 'id',
                            displayField: 'nome',
                            store: new Ext.data.JsonStore({
                                autoLoad: true,
                                root: 'result',
                                totalProperty: 'total',
                                fields: ['id', 'nome'],
                                proxy: new Ext.data.HttpProxy({
                                    method: 'GET',
                                    url: action('CMS/get_counties/json')
                                })
                            })
                        },
                        {
                            layout: 'column',
                            border: false,
                            items: [
                                {
                                    layout: 'form',
                                    border: false,
                                    items: [combo]
                                },
                                {
                                    layout: 'form',
                                    bodyStyle: 'margin: 19px 0 0 7px;',
                                    border: false,
                                    items: [addButton]
                                }
                            ]
                        },
                        {
                            fieldLabel: 'Data de protocolo',
                            name: 'start_date',
                            value: opts.vals.start_date || '',
                            format: 'd/m/Y',
                            xtype: 'datefield'
                        },
                        {
                            fieldLabel: 'Decisão final',
                            name: 'decision_date',
                            value: opts.vals.decision_date || '',
                            format: 'd/m/Y',
                            xtype: 'datefield'
                        },
                        new toolkit.plugins.CKEditor({
                            name: 'filing',
                            fieldLabel: 'Observações',
                            value: toolkit.util.replaceAll(opts.vals.filing, '\\', '') || '',
                            toolbar: [
                                ['PasteFromWord'],
                                ['Link','Unlink'],
                                ['NumberedList','BulletedList'],
                                ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
                            ],
                            autoScroll: true,
                            width: 600,
                            height: 100
                        }),
                        new toolkit.plugins.CKEditor({
                            name: 'text',
                            fieldLabel: 'Síntese dos fatos',
                            value: toolkit.util.replaceAll(opts.vals.text, '\\', '') || '',
                            toolbar: [
                                ['PasteFromWord'],
                                ['Link','Unlink'],
                                ['NumberedList','BulletedList'],
                                ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
                            ],
                            autoScroll: true,
                            width: 600,
                            height: 250
                        })
                    ]
                }
            });
        }

    });
}
