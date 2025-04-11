if(!toolkit.web.cms.Attachments)
{
    toolkit.web.cms.Attachments = Ext.extend(Ext.Window, {
        constructor: function(post, post_title)
        {
            this.post = post;
            this.post_title = post_title;
            this.kind = 'Image';
            this.kind_normalize = {
                'Image': 'Imagem',
                'File': 'Arquivo',
                'Video': 'Vídeo'
            };

            var options = {
                title: 'Imagens anexadas à '+this.post_title,
                region: 'center',
                modal: true,
                layout: 'fit',
                defaults: {margins: '2 2 2 2'}
            };

            toolkit.web.cms.Attachments.superclass.constructor.call(this, options);

            var store_options = {
                autoLoad: true,
                root: 'result',
                totalProperty: 'total',
                remoteSort: true,
                fields: ['id', 'title', 'slug', 'credits', 'embed', 'url', 'position', 'is_public'],
                url: action('CMS/get_attachments/json'),
                baseParams: { start: 0, limit: 300, post: this.post, kind: this.kind, exclude: 0 },
                scope: this,
                listeners: {
                    load: function()
                    {
                        if(this.kind == 'File')
                            Ext.select('.media-wrap img').set({src: icons+'file-thumb.png'});

                        Ext.select('.media-item .athenas-edit').on('click',
                            function(event, el)
                            {
                                var record = this.store_related.getAt( Ext.select('.media-item .athenas-edit').indexOf(Ext.get(el)) );
                                var title = this.kind_normalize[this.kind];
                                this.makeForm({
                                    title: 'Editar '+title,
                                    vals: {
                                        post: this.post,
                                        kind: this.kind,
                                        id: record.get('id'),
                                        embed: record.get('embed'),
                                        title: record.get('title'),
                                        credits: record.get('credits'),
                                        public_access: record.get('is_public'),
                                        position: record.get('position'),
                                        url: record.get('url')
                                    }
                                }).show();
                            },
                            this
                        );
                        Ext.select('.media-item .athenas-delete').on('click',
                            function(event, el)
                            {
                                var record = this.store_related.getAt( Ext.select('.media-item .athenas-delete').indexOf(Ext.get(el)) ),
                                    store = this.store_related,
                                    model = this.kind,
                                    post = this.post;

                                 xConfirm({
                                    title: 'Confirmação',
                                    msg: 'Confirma a exclusão do anexo: '+ record.get('title') +' ?',
                                    fn: function(btn)
                                    {
                                        deleteItem({
                                            signal: btn,
                                            model: model,
                                            rel_id: post,
                                            pars: record.get('id'),
                                            store: store
                                        });
                                    }
                                });
                            },
                            this
                        );
                    },
                    scope: this
                }
            };

            this.store_related = new Ext.data.JsonStore(store_options);

            new Ext.LoadMask(Ext.getBody(), {msg: 'Por favor aguarde...', store: this.store_related});
            this.add(this.getAttachments());
            this.doLayout();
        },

        getAttachments: function()
        {
            if(!this.medias)
            {
                this.medias = new Ext.Panel({
                    layout: 'fit',
                    height: 320,
                    width: 505,
                    autoScroll: true,
                    scope: this,
                    tbar: [
                        {
                            tooltip: 'Novo anexo',
                            icon: icons+'add.png',
                            text: 'Novo',
                            handler: function()
                            {
                                var title = this.kind_normalize[this.kind];
                                this.makeForm({
                                    title: 'Adicionar '+title,
                                    vals: {
                                        post: this.post,
                                        kind: this.kind,
                                        position: 9999,
                                        public_access: true
                                    }
                                }).show();
                            },
                            scope:this
                        },
                        '-',
                        {
                            tooltip: 'Visualizar imagens anexadas',
                            icon: icons+'image.png',
                            text: 'Imagens',
                            handler: function()
                            {
                                this.kind = 'Image';
                                this.setTitle('Imagens anexadas à '+this.post_title);
                                this.store_related.load({
                                    params: {
                                        kind:this.kind,
                                        'image-width': 110,
                                        'image-cut-mode': 'square'
                                    }
                                });
                            },
                            scope:this
                        },
                        {
                            tooltip: 'Visualizar vídeos anexados',
                            icon: icons+'video.png',
                            text: 'Vídeos',
                            handler: function()
                            {
                                this.kind = 'Video';
                                this.setTitle('Vídeos anexados à '+this.post_title);
                                this.store_related.load({
                                    params: {
                                        kind:this.kind,
                                        'image-width': 110,
                                        'image-cut-mode': 'square'
                                    }
                                });
                            },
                            scope:this
                        },
                        {
                            tooltip: 'Visualizar arquivos anexadas',
                            icon: icons+'file.png',
                            text: 'Arquivos',
                            handler: function()
                            {
                                this.kind = 'File';
                                this.setTitle('Arquivos anexados à '+this.post_title);
                                this.store_related.load({params: {kind: this.kind}});
                            },
                            scope:this
                        }
                    ],
                    items: new Ext.DataView({
                        store: this.store_related,
                        autoHeight: true,
                        multiSelect: true,
                        overClass: 'media-item-hover',
                        itemSelector: '.media-item',
                        emptyText: 'Sem itens para exibir.',
                        tpl: new Ext.XTemplate(
                            '<tpl for=".">',
                                '<div class="media-item">',
                                    '<div class="media-wrap">',
                                        '<img src="{url}" alt="{title}" ext:qtip="{title}">',
                                    '</div>',
                                    '<div class="media-action">',
                                        '<span class="athenas-delete">Excluir</span>',
                                        '<span class="athenas-edit">Editar</span>',
                                        '<tpl if="!is_public">',
                                            '<span class="athenas-protected" title="Arquivo protegido, acesso restrito.">Arquivo protegido, acesso restrito.</span>',
                                        '</tpl>',
                                    '</div>',
                                    '<span class="media-title">{title}</span>',
                                '</div>',
                            '</tpl>'
                        )
                    })
                });
            }
            return this.medias;
        },

        makeForm: function(opts)
        {
            var hidden = [
                {
                    name: 'post',
                    value: opts.vals.post || '',
                    xtype: 'hidden'
                },
                {
                    name: 'kind',
                    value: opts.vals.kind || '',
                    xtype: 'hidden'
                },
                {
                    name: 'id',
                    value: opts.vals.id || '',
                    xtype: 'hidden'
                }
            ];


            var common = [
                {
                    name: 'title',
                    fieldLabel: 'Nome',
                    value: opts.vals.title || '',
                    xtype: 'textfield',
                    width: 370
                },
                {
                    name: 'position',
                    fieldLabel: 'Posição',
                    value: opts.vals.position || '',
                    xtype: 'textfield',
                    width: 50
                },
                {
                    name: 'public_access',
                    fieldLabel: 'Acesso público',
                    checked: opts.vals.public_access,
                    value: opts.vals.public_access,
                    xtype: 'checkbox',
                    width: 50
                }
            ];

            if(opts.vals.kind != 'File')
            {
                common.splice(1, 0, {
                    name: 'credits',
                    fieldLabel: 'Créditos',
                    value: opts.vals.credits || '',
                    xtype: 'textfield',
                    width: 225
                });
            }

            var media = [
                {
                    name: 'upfile',
                    fieldLabel: (this.kind == 'Video') ? 'Imagem de capa' : this.kind_normalize[this.kind],
                    xtype: 'fileuploadfield',
                    width: 370
                }
            ];

            if(this.kind == 'Video')
            {
                media[media.length] = {
                    name: 'url_embed',
                    fieldLabel: 'Código do serviço de vídeo',
                    value: toolkit.util.replaceAll(opts.vals.embed, '\\', '') || '',
                    xtype: 'textfield',
                    width: 370
                };
            }

            return ExtFormHelper({
                url: action('CMS/add_or_edit_attachment/json'),
                store: this.store_related,
                windowConfig: {
                    title: opts.title
                },
                formConfig: {
                    autoWidth: true,
                    autoHeight: true,
                    fileUpload: true,
                    items: media.concat(hidden, common)
                }
            });
        },

        kindFormDisplay: function(kind, url)
        {
            var options = {
                'Image': (url) ? '<img src="'+url+'">' : '',
                'File': (url) ? '<a style="display:block;" href="'+url+'">'+url+'</a>' : ''
            }
            return options[kind];
        }
    });
}
