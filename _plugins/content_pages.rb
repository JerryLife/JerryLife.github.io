# Apply editable page metadata before navigation, SEO, and page layouts render.
Jekyll::Hooks.register :site, :post_read do |site|
  content = site.data.fetch("content")
  pages = content.fetch("pages")
  site.pages.each do |page|
    key = page.data["content_key"]
    next unless key

    copy = pages.fetch(key)
    %w[title description nav nav_order].each do |field|
      page.data[field] = copy[field] if copy.key?(field)
    end
    page.data["copy"] = copy
    if key == "cv"
      page.data["nav_url"] = content.fetch("site").fetch("links").fetch("cv")
      page.data["cv_pdf"] = page.data["nav_url"]
    end
  end
end
